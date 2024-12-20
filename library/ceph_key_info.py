#!/usr/bin/python3

from ansible.module_utils.basic import AnsibleModule
import os
import json

def main():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(required=True),
            cluster=dict(required=False, default='ceph'),
            user=dict(required=False),
            user_key=dict(required=False, type='path'),
            output_format=dict(required=False, default='json'),
            state=dict(required=False, default='info'),
            containerized=dict(required=False, default=True, type='bool'),
            container_image=dict(required=False)
        ),
        supports_check_mode=True
    )

    result = dict(
        changed=False,
        rc=2,
        stdout='',
        stderr=''
    )

    user_key = module.params.get('user_key')
    if user_key and os.path.exists(user_key):
        result['rc'] = 0
        result['stdout'] = '{"exists": true}'
    
    module.exit_json(**result)

if __name__ == '__main__':
    main()
