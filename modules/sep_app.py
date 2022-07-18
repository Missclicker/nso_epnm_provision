from __main__ import app

from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class SEP(db.Model):
    sep_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), nullable=False)
    rtr_name = db.Column(db.String(60), nullable=False)
    port = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return f'SEP {self.name}'


@app.route('/seps')
def show_seps():
    seps = SEP.query.all()
    sep_dict = {}
    for sep in seps:
        if not sep.name in sep_dict:
            sep_dict[sep.name] = [sep.rtr_name, sep.port]
        else:
            sep_dict[sep.name].extend([sep.rtr_name, sep.port])
    return render_template(
        'sep.html', seps=sep_dict, title='ALL SEP RINGS'
    )


@app.route('/<sep_name>/edit')
def edit_sep(sep_name):
    pass
