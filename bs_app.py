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

@app.route('/')
def index():
    return render_template("test.html", column_names=df.columns.values, row_data=list(df.values.tolist()),
                           link_column="BS", zip=zip, title='BS Deploy table')


if __name__ == '__main__':
    df = normalize_crossing(FILE)
    df['deployed_on'] = DEPLOY_STATUS
    df = df.reset_index()
    app.run(debug=True, port=4949)
