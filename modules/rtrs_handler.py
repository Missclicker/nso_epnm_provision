import netmiko
# from ipaddress import ip_address, IPv4Address


class RTR:
    def __init__(self, ip: str, user: str, password: str, init_connect=False):
        self.ip = ip
        self.__connect_data = {
            "device_type": "cisco_xr",
            "ip": ip,
            "username": user,
            "password": password,
        }
        self.templates = {
            'route': 'templates/textFSM/cisco_xr_show_ip_route.textfsm',
            'brief': 'templates/textFSM/cisco_xr_show_interface_brief.textfsm'
        }
        if init_connect:
            self.connect()
        else:
            self.ssh = None

    def connect(self):
        self.ssh: netmiko.BaseConnection = netmiko.ConnectHandler(**self.__connect_data)

    def connect_decorator(self, func):
        self.connect()
        return func

    @connect_decorator
    def check_route(self, net: str, vrf: str) -> bool:
        cli_text = self.ssh.send_command(f'show route vrf {vrf} {net}')
        if 'Network not in table' in cli_text:
            return False
        else:
            return True

    @connect_decorator
    def get_connected_networks(self) -> dict:
        data = self.ssh.send_command('show ipv4 interface brief',
                                     use_textfsm=True, textfsm_template=self.templates['brief'])
        subnets_dict = {}
        for i in data:
            if i['vrf'] in subnets_dict:
                subnets_dict[i['vrf']].update({
                    i['ip']: [i['ifname'], i['int_state']]
                })
            else:
                subnets_dict[i['vrf']] = {
                    i['ip']: [i['ifname'], i['int_state']]
                }
        return subnets_dict
