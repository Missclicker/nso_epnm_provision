import pandas as pd


def normalize_crossing(file_name):
    data = pd.read_excel(file_name)
    data = data[
        ['BS', 'vlan', 'DESCRIPTION', 'VRF', 'Service', 'NCS', 'NEW_PORT', 'ip_address', 'gw', 'mask', 'bs', 'Type']
    ]
    columns = ['BS', 'vlan', 'description', 'vrf', 'service', 'ncs', 'port', 'ipv4', 'gw', 'mask', 'bs', 'bs_type']
    data.columns = columns
    # drop empty vlans and BSes with iface on two+ BSes
    empty_vlans_on_bs = data[data.vlan.isna()].BS
    temp_bs_ports = data.groupby(['BS', 'NEW_PORT']).size()
    diff_ports_on_bs = temp_bs_ports[temp_bs_ports.index.get_level_values(0).duplicated()].index.get_level_values(0)

    data = data[~(
            (data['BS'].isin(empty_vlans_on_bs))
            | (data['BS'].isin(diff_ports_on_bs))
    )]
    data['vlan'] = data.vlan.astype(int)

    # fix empty descriptions
    data['description'] = data.apply(lambda x: x['description'].strip('- ').replace('To ', '') if type(
        x['description']) == str else f"BS {x['BS']}", axis=1)
    data = data.set_index(['BS', 'vlan'])

    return data


if __name__ == '__main__':
    df = normalize_crossing('Data_files/crossing_test.xlsx')
