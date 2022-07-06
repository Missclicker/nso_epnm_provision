import click
import pandas as pd
from Data_files.base_data import *
from epnm import EPNM
from normalize_data import normalize_crossing

FILE = 'Data_files/crossing_test.xlsx'
DEPLOY_STATUS = pd.read_csv('bs_status.csv', index_col=['bs_id', 'vlan'])

epnm = EPNM(base_url)
data = normalize_crossing(FILE)
bs_id = "6035"
data_dict = {
    'bs_id': bs_id,
    'vlans': data.loc[bs_id].index.to_list()
}
data_dict.update(data.loc[bs_id][['ncs', 'port', 'description', 'vrf', 'ipv4', 'gw', 'mask']].to_dict(orient='list'))


def print_bases(bs_data: pd.DataFrame, deploy_cache: pd.DataFrame) -> None:
    data['deployed_on'] = deploy_cache
    pd.set_option('display.max_columns', 10)
    print(data[['bs_type', 'service', 'description', 'ncs', 'port', 'deployed_on']].to_markdown())


print(data_dict)
