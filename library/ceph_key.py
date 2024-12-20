#!/usr/bin/python3

from ansible.module_utils.basic import AnsibleModule
import os
import subprocess

def generate_secret():
    """Generate a random secret key"""
    cmd = ['ceph-authtool', '--gen-print-key']
    return subprocess.check_output(cmd).strip()

def generate_caps(type, caps):
    """Convert caps dictionary to command line arguments"""
    cmd = []
    if type == "ceph-authtool":
        for k, v in caps.items():
            cmd.extend(['--cap', k, v])
    else:
        for k, v in caps.items():
            cmd.extend([k, v])
    return cmd

def generate_ceph_authtool_cmd(cluster, name, secret, caps, file_destination, container_image=None):
    """Generate ceph-authtool command"""
    cmd = []
    
    if container_image:
        cmd.extend([
            'docker', 'run', '--rm', '--net=host',
            '-v', '/etc/ceph:/etc/ceph:z',
            '-v', '/var/lib/ceph/:/var/lib/ceph/:z',
            '-v', '/var/log/ceph/:/var/log/ceph/:z',
            '--entrypoint=ceph-authtool',
            container_image
        ])
    else:
        cmd.append('ceph-authtool')

    # 디렉토리 생성
    os.makedirs(os.path.dirname(file_destination), exist_ok=True)

    cmd.extend(['--create-keyring', file_destination])
    
    if name:
        cmd.extend(['--name', name])
    if secret:
        cmd.extend(['--add-key', secret])
    if caps:
        cmd.extend(generate_caps("ceph-authtool", caps))

    return cmd

def main():
    module = AnsibleModule(
        argument_spec=dict(
            cluster=dict(required=False, default='ceph'),
            name=dict(required=True),
            state=dict(required=False, default='present', choices=['present', 'absent', 'generate_secret']),
            secret=dict(required=False),
            caps=dict(required=False, type='dict', default=None),
            dest=dict(required=False),
            import_key=dict(required=False, type='bool', default=False),
            owner=dict(required=False),
            group=dict(required=False),
            mode=dict(required=False),
            containerized=dict(required=False, type='bool', default=True),
            container_image=dict(required=False, default='quay.io/ceph/ceph:v17')
        ),
        supports_check_mode=True
    )

    result = dict(
        changed=False,
        stdout='',
        stderr='',
        rc=0,
        cmd=None
    )

    state = module.params.get('state')
    
    if state == 'generate_secret':
        secret = generate_secret()
        result['stdout'] = secret.decode()
        result['changed'] = True
    elif state == 'present':
        dest = module.params.get('dest')
        if dest:
            cmd = generate_ceph_authtool_cmd(
                module.params['cluster'],
                module.params['name'],
                module.params['secret'],
                module.params['caps'],
                os.path.join(dest, f"{module.params['cluster']}.{module.params['name']}.keyring"),
                module.params['container_image'] if module.params['containerized'] else None
            )
            
            result['cmd'] = cmd
            rc, out, err = module.run_command(cmd)
            result['rc'] = rc
            result['stdout'] = out
            result['stderr'] = err
            if rc != 0:
                module.fail_json(msg='Failed to create key', **result)
            result['changed'] = True

    module.exit_json(**result)

if __name__ == '__main__':
    main()
