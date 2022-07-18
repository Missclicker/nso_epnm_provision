import pandas as pd
from flask import Flask, render_template, request, redirect, url_for
from normalize_data import normalize_crossing
from bs_app_cli import bs_action

app = Flask(__name__)

FILE = 'Data_files/crossing_test.xlsx'
DEPLOY_FILE = 'bs_status.csv'
DEPLOY_STATUS = pd.read_csv(DEPLOY_FILE, index_col=['bs_id', 'vlan'])
DF = normalize_crossing(FILE)
DF['deployed_on'] = DEPLOY_STATUS
DF = DF.reset_index()


# TODO refresh function & page

@app.route('/')
def index():
    main_data = DF[['BS', 'vlan', 'bs_type', 'service', 'description', 'port', 'ncs', 'deployed_on']]
    main_data.columns = ['BS', 'vlan', 'bs_type', 'service', 'description', 'port', 'CSG-id', 'deployed_on']
    return render_template(
        "main_page.html",
        column_names=main_data.columns.values,
        row_data=list(
            main_data.values.tolist()
        ),
        link_column="BS", zip=zip, title='BS Deploy table'
    )


@app.route('/deploy', methods=['POST'])
def deploy():
    bs_id = request.form['bs_id']
    one_bs = DF.set_index(['BS', 'vlan']).loc[bs_id]
    if not one_bs['deployed_on'].notna().all():
        template = 'create_subs'
        one_bs['deployed_on'] = one_bs['deployed_on'].astype(str).apply(lambda x: x.replace('.0', ''))
        operation_result = bs_action(template, one_bs, bs_id)
        if operation_result:
            refresh_cache()
    return redirect(url_for('bs_page', bs_id=bs_id))


@app.route('/delete', methods=['POST'])
def delete():
    bs_id = request.form['bs_id']
    one_bs = DF.set_index(['BS', 'vlan']).loc[bs_id]
    if not one_bs['deployed_on'].isna().all():
        template = 'remove_subs'
        one_bs['deployed_on'] = one_bs['deployed_on'].astype(str).apply(lambda x: x.replace('.0', ''))
        operation_result = bs_action(template, one_bs, bs_id)
        if operation_result:
            refresh_cache()
    return redirect(url_for('bs_page', bs_id=bs_id))


@app.route('/<bs_id>')
def bs_page(bs_id):
    one_bs = DF[DF['BS'] == bs_id][[
        'vlan', 'ncs', 'deployed_on', 'description', 'vrf', 'service', 'port', 'ipv4',
        'gw', 'mask', 'bs', 'bs_type',
    ]].fillna('-')

    one_bs['deployed_on'] = one_bs['deployed_on'].astype(str).apply(lambda x: x.replace('.0', ''))

    return render_template(
        'bs.html',
        title=bs_id,
        column_names=one_bs.columns.values,
        row_data=list(one_bs.values.tolist()),
        zip=zip
    )


@app.route('/api/data')
def data():
    main_df = DF[[
        'BS', 'vlan', 'bs_type', 'service', 'description', 'ncs', 'port', 'deployed_on'
    ]].fillna("-")
    main_df['deployed_on'] = main_df['deployed_on'].astype(str).apply(lambda x: x.replace('.0', ''))
    return {'data': main_df.to_dict(orient='records')}


def refresh_cache() -> None:
    global DEPLOY_STATUS, DF
    DEPLOY_STATUS = pd.read_csv(DEPLOY_FILE, index_col=['bs_id', 'vlan'])
    DF = normalize_crossing(FILE)
    DF['deployed_on'] = DEPLOY_STATUS
    DF = DF.reset_index()


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=4949)
