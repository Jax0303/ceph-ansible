from ansible.errors import AnsibleFilterError
from ansible.module_utils.common.text.converters import to_native
from netaddr import IPNetwork, IPAddress

def ips_in_ranges(addresses, networks):
    if not isinstance(addresses, list):
        raise AnsibleFilterError('addresses must be a list')
    if not isinstance(networks, list):
        raise AnsibleFilterError('networks must be a list')
    
    result = []
    for address in addresses:
        for network in networks:
            try:
                if IPAddress(address) in IPNetwork(network):
                    result.append(address)
            except Exception as e:
                raise AnsibleFilterError('Error processing IP: %s' % to_native(e))
    return result

class FilterModule(object):
    def filters(self):
        return {
            'ips_in_ranges': ips_in_ranges
        } 