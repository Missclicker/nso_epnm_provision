from time import sleep

import requests
import urllib3
from modules.test_response import Response

urllib3.disable_warnings()


class EPNM:

    def __init__(self, base_url):
        if 'https' not in base_url:
            self.testing = True
        else:
            self.testing = False
        self.base_url = base_url
        self.remove_subs_template_name = 'SUBs_REMOVAL'
        self.create_subs_template_name = 'L3_SUBS_CREATION'
        self.create_pw_template_name = 'CREATE_P2P_PW'

    def testing_decorator(func):
        def wrapper(self, *args, **kwargs):
            if not self.testing:
                return func(self, *args, **kwargs)
            print('Imitating connection ...')
            sleep(2)
            r = Response()
            return r

        return wrapper

    @testing_decorator
    def __base_get__(self, url, timeout=None):
        return requests.get(self.base_url + url, timeout=timeout, verify=False)

    @testing_decorator
    def __base_put__(self, url, data, timeout=None):
        return requests.put(self.base_url + url, json=data, timeout=timeout, verify=False)

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
            # to reach template names use:
            # [i['cliTemplateDTO']['name'] for i in r.json()['queryResponse']['entity']]
            return r.json()
        else:
            return {'Error': r.content}

    def push_template(self, template_name: str, **kwargs) -> dict:
        url = '/webacs/api/v4/op/cliTemplateConfiguration/deployTemplateThroughJob.json'
        data = self.generate_json(template_name, **kwargs)
        if 'Error' in data.keys():
            return data
        r = self.__base_put__(url, data)
        if r.ok:
            return r.json()
        else:
            return {'Error': r.content}

    def check_job(self, job_json) -> bool:
        job_status = r = 'RUNNING'
        url = '/webacs/api/v4/op/jobService/runhistory.json?jobName=' \
              f'{job_json["mgmtResponse"]["cliTemplateCommandJobResult"][0]["jobName"]}'
        while job_status in str(r):
            r = self.__base_get__(url, timeout=10).json()
            sleep(1)
        if "1/1 template configurations successfully applied" in str(r):
            return True
        else:
            return False

    def get_rtr_config(self, rtr_json):
        def config_url(dev_name):
            return f'/webacs/api/v4/data/ConfigVersions.json?.full=true&deviceName=%22{dev_name}%22&.sort=-createdAt' \
                   f'&.maxResults=1 '

        def config_download(f_id):
            return f'/webacs/api/v4/op/configArchiveService/extractSanitizedFile.json?fileId={f_id}'

        r = self.__base_get__(config_url(rtr_json['devicesDTO']['deviceName']))
        # TODO check if config links are always in the same order or add check "admin/device config"
        file_id = r.json()['queryResponse']['entity'][0]['configVersionsDTO']['fileInfos']['fileInfo'][0]['fileId']
        config = self.__base_get__(config_download(file_id)).content
        return config

    def generate_json(self, template_name: str = "", **kwargs) -> dict:
        if template_name == "remove_subs":
            return self._json_remove_subs(**kwargs)
        elif template_name == "create_subs":
            return self._json_create_subs(**kwargs)
        else:
            return {'Error': 'Please, provide template_name'}

    def _json_remove_subs(self, pe_id: int = 0, bs_data: dict = None, shut_parent: int = 0) -> dict:
        # TODO delete description from main int if no other subs
        if not pe_id or not bs_data:
            return {'Error': 'Please, provide data'}
        vlans = ','.join([str(x) for x in bs_data['vlans']])
        ifname = bs_data['port'][0]
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

    def _json_create_subs(self, pe_id: int = None, bs_data: dict = None) -> dict:
        if not pe_id or not bs_data:
            return {'Error': 'Please, provide data'}
        vlans = ','.join([str(x) for x in bs_data['vlans']])
        ifname = bs_data['port'][0]
        description = bs_data['description'][0]
        vrfs = ','.join(bs_data['vrf'])
        gws = ','.join(bs_data['gw'])
        smasks = ','.join(bs_data['mask'])
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
                                "value": vrfs
                            }, {
                                "name": "GWs",
                                "value": gws
                            }, {
                                "name": "SMasks",
                                "value": smasks
                            }
                            ]
                        }
                    }
                    ]
                },
                "templateName": self.create_subs_template_name
            }
        }
