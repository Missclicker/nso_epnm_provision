import pandas as pd
from flask import Flask, render_template
from normalize_data import normalize_crossing

app = Flask(__name__)

# class BS:
#     def __init__(self):

FILE = 'Data_files/crossing_test.xlsx'
DEPLOY_FILE = 'bs_status.csv'
DEPLOY_STATUS = pd.read_csv(DEPLOY_FILE, index_col=['bs_id', 'vlan'])
DEPLOY_STATUS.deployed_on = DEPLOY_STATUS.deployed_on.astype(str)
DF = normalize_crossing(FILE)
DF['deployed_on'] = DEPLOY_STATUS
DF = DF.reset_index()

@app.route('/')
def index():
    return render_template(
        "test.html",
        column_names=DF[[
            'BS', 'vlan', 'bs_type', 'service', 'description', 'ncs', 'port', 'deployed_on'
        ]].columns.values,
        row_data=list(DF.values.tolist()),
        link_column="BS", zip=zip, title='BS Deploy table'
    )


# @app.route('/data/<bs_id>')
# def data(bs_id):
#

@app.route('/api/data')
def data():
    return {'data': DF[[
        'BS', 'vlan', 'bs_type', 'service', 'description', 'ncs', 'port', 'deployed_on'
    ]].fillna("").to_dict(orient='records')}


if __name__ == '__main__':
    app.run(debug=True, port=4949)
