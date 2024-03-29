import pandas as pd
from modules.epnm import EPNM
try:
    from Data_files.base_data import *
except ModuleNotFoundError:
    base_url = 'just_for_test'


FILE = 'Data_files/crossing_test.xlsx'
DEPLOY_FILE = 'bs_status.csv'
DEVICES = pd.read_excel('Data_files/SITE_XH mapping.xlsx')
DEPLOY_STATUS = pd.read_csv(DEPLOY_FILE)
DEPLOY_STATUS['bs_id'] = DEPLOY_STATUS['bs_id'].astype(str)
DEPLOY_STATUS = DEPLOY_STATUS.set_index(['bs_id', 'vlan'])
epnm = EPNM(base_url)



def chose_bs(bs_data: pd.DataFrame, deploy_cache: pd.DataFrame) -> bool:
    bs_data['deployed_on'] = deploy_cache
    to_print = bs_data[['bs_type', 'service', 'description', 'ncs', 'port', 'deployed_on']].reset_index()
    print(to_print.to_markdown(index=True))
    bs_num = input('select BS number ->')
    try:
        bs_num = int(bs_num)
    except ValueError:
        print("Thanks for working!")
        exit()

    chosen_bs_id = bs_data.reset_index().iloc[bs_num]['BS']
    return chose_operation(bs_data.loc[chosen_bs_id], chosen_bs_id, from_cli=True)


def refresh_cache(vlans: list, bs_id: str, operation: bool, ncs: int = 0):
    global DEPLOY_STATUS
    if operation:
        for vlan in vlans:
            DEPLOY_STATUS.loc[(bs_id, vlan), :] = ncs
    else:
        DEPLOY_STATUS = DEPLOY_STATUS.reset_index()[
            DEPLOY_STATUS.reset_index().bs_id != bs_id
            ].set_index(['bs_id', 'vlan'])
    DEPLOY_STATUS.sort_index().to_csv(DEPLOY_FILE)


def dict_from_df(df: pd.DataFrame, bs_id: str) -> dict:
    data_dict = {
        'bs_id': bs_id,
        'vlans': df.index.to_list()
    }
    data_dict.update(
        df[['ncs', 'port', 'description', 'vrf', 'ipv4', 'gw', 'mask']].to_dict(orient='list')
    )
    return data_dict


def get_pe_id(rtr_ip: str) -> int:
    devices = epnm.get_devices()['queryResponse']['entity']
    pe_id = 0
    for dev in devices:
        if 'devicesDTO' in dev.keys() and dev['devicesDTO']['ipAddress'] == rtr_ip:
            pe_id: int = dev['devicesDTO']['@id']
            break
    if not pe_id:
        raise ValueError(f'Router {rtr_ip} not found on EPNM')
    return pe_id


def chose_operation(one_bs: pd.DataFrame, bs_id: str, from_cli: bool = False) -> bool:
    if one_bs.deployed_on.isna().all():
        print('This service was not deployed, checking on router')

        if check_router(one_bs):
            # TODO set cache to "deployed"
            pass
            return True
        else:
            template = 'create_subs'
            deploy_dict = dict_from_df(one_bs, bs_id)
    else:
        # check if all vlans are deployed on router according to "crossing"
        if (one_bs['ncs'] == one_bs['deployed_on']).all():
            if from_cli:
                print('BS already deployed according to crossing')
                print('Do you want to delete BS from router?')
                answer = input("Y/n > ")
                if 'n' in answer.lower():
                    print('exiting')
                    return True

            print('Deleting BS...')
            template = 'remove_subs'
        else:
            # deploy only those vlans which are not on RTR
            # to_deploy = one_bs[one_bs['ncs'] == one_bs['deployed_on']]
            template = 'create_subs'
    bs_action(template, one_bs, bs_id)


def bs_action(template: str, df: pd.DataFrame, bs_id: str):
    deploy_dict = dict_from_df(df, bs_id)
    deploy_result = bs_deploy(deploy_dict, template)
    if deploy_result:
        if template == 'create_subs':
            refresh_cache(deploy_dict['vlans'], bs_id, True, ncs=deploy_dict['ncs'][0])
        else:
            refresh_cache(deploy_dict['vlans'], bs_id, False)
    return deploy_result


def bs_deploy(deploy_dict: dict, template) -> bool:
    rtr_ip = DEVICES[DEVICES.Hostname.str.endswith(str(deploy_dict['ncs'][0]))]['Loopback0'].to_string(index=False)
    pe_id = get_pe_id(rtr_ip)
    creation_job = epnm.push_template(template, pe_id=pe_id, bs_data=deploy_dict)
    print('Job pushed, waiting for registration...')
    return epnm.check_job(creation_job)
