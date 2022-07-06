import requests
import urllib3

urllib3.disable_warnings()


class EPNM:

    def __init__(self, base_url):
        self.base_url = base_url
        self.remove_subs_template_name = 'SUBs_REMOVAL'
        self.create_subs_template_name = 'CREATE_L3_SUBS'
        self.create_pw_template_name = 'CREATE_P2P_PW'

    def __base_get__(self, url):
        return requests.get(self.base_url + url, verify=False)

    def get_devices(self):
        url = '/webacs/api/v4/data/Devices.json?.full=true'
        r = self.__base_get__(url)
        if r.ok:
            return r.json()
        else:
            return {'Error': r.content}

    def get_templates(self):
        url = '/webacs/api/v4/data/CliTemplate.json?.full=true&path=contains("User Defined")'
        r = self.__base_get__(url)
        if r.ok:
            return r.json()
        else:
            return {'Error': r.content}

    def push_template(self, template_name: str) -> dict:
        url = '/webacs/api/v4/op/cliTemplateConfiguration/deployTemplateThroughJob.json'
        data = self.generate_json(template_name)
        if 'Error' in data.keys():
            return data
        r = requests.put(self.base_url + url, json=data, verify=False)
        if r.ok:
            return r.json()
        else:
            return {'Error': r.content}

    def check_job(self, job_name):
        pass

    def get_device_config(self):
        pass

    def generate_json(self, template_name: str = "", **kwargs) -> dict:
        if template_name == "remove_subs":
            return self._json_remove_subs(kwargs)
        elif template_name == "create_subs":
            return self._json_create_subs(kwargs)
        else:
            return False  # {'Error': 'Please, provide template_name'}

    def _json_remove_subs(self, pe_id: int = 0, bs_data: dict = {}, shut_parent: int = 0) -> dict:
        if not pe_id or not bs_data:
            return {'Error': 'Please, provide data'}
        vlans = bs_data['vlans']
        ifname = bs_data['NEW_PORT'][0]
        return {
            "cliTemplateCommand": {
                "options": {
                    "copyConfigToStartup": False
                },
                "targetDevices": {
                    "targetDevice": [{
                        "targetDeviceID": pe_id,
                        "variableValues": {
                            "variableValue": [{
                                "name": "ifName",
                                "value": ifname
                            }, {
                                "name": "shutParent",
                                "value": shut_parent
                            }, {
                                "name": "Vlans",
                                "value": vlans
                            }
                            ]
                        }
                    }
                    ]
                },
                "templateName": self.remove_subs_template_name
            }
        }

    def _json_create_subs(self, pe_id: int = None, bs_data: dict = {}) -> dict:
        if not pe_id or not bs_data:
            return {'Error': 'Please, provide data'}
        vlans = bs_data['vlans']
        ifname = bs_data['NEW_PORT']
        description = bs_data['DESCRIPTION']
        return {
            "cliTemplateCommand": {
                "options": {
                    "copyConfigToStartup": False
                },
                "targetDevices": {
                    "targetDevice": [{
                        "targetDeviceID": pe_id,
                        "variableValues": {
                            "variableValue": [{
                                "name": "ifName",
                                "value": ifname
                            }, {
                                "name": "parentDescription",
                                "value": description
                            }, {
                                "name": "Vlans",
                                "value": vlans
                            }, {
                                "name": "VRFs",
                                "value": VRFs
                            }, {
                                "name": "GWs",
                                "value": GWs
                            }, {
                                "name": "SMasks",
                                "value": SMasks
                            }
                            ]
                        }
                    }
                    ]
                },
                "templateName": self.create_subs_template_name
            }
        }
