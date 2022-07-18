from __main__ import app

from flask import render_template, redirect, url_for, request
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


class RTRS(db.Model):
    rtr_id = db.Column(db.Integer, primary_key=True)
    rtr_name = db.Column(db.String(60), unique=True, nullable=False)
    ip = db.Column(db.String(60), unique=True, nullable=False)

    def __repr__(self):
        return f'RTR {self.rtr_name}'


def fill_sep_database():
    # TODO duplicate validation, data validation - including router interfaces
    for i in [1, 2]:
        sep = SEP(
            name=request.form['sep_name'],
            rtr_name=request.form[f'side_{i}'],
            port=request.form[f'port_{i}']
        )
        db.session.add(sep)
    db.session.commit()


def create_seps_dict(seps: list) -> dict:
    sep_dict = {}
    for sep in seps:
        if not sep.name in sep_dict:
            sep_dict[sep.name] = [sep.rtr_name, sep.port]
        else:
            sep_dict[sep.name].extend([sep.rtr_name, sep.port])
    return sep_dict


@app.route('/seps')
def show_seps():
    seps = SEP.query.all()
    sep_dict = create_seps_dict(seps)
    return render_template(
        'sep.html', seps=sep_dict, title='ALL SEP RINGS'
    )


@app.route('/seps/<sep_name>/edit', methods=('GET', 'POST'))
def edit_sep(sep_name):
    seps = SEP.query.filter_by(name=sep_name).all()
    if request.method == 'POST':
        for i, sep in zip ([1,2], seps):
            sep.name = request.form['sep_name']
            sep.rtr_name = request.form[f'side_{i}']
            sep.port = request.form[f'port_{i}']
        db.session.commit()
        return redirect(url_for('show_seps'))

    return render_template(
        'sep_edit.html', seps=seps, rtrs=[rtr.rtr_name for rtr in RTRS.query.all()]
    )


@app.route('/seps/create', methods=('GET', 'POST'))
def create_sep():
    if request.method == 'POST':
        fill_sep_database()
        return redirect(url_for('show_seps'))

    return render_template('sep_create.html',
                           title='Add new SEP to DB', rtrs=[rtr.rtr_name for rtr in RTRS.query.all()])


@app.post('/seps/<sep_name>/delete')
def delete_sep(sep_name):
    seps = SEP.query.filter_by(name=sep_name).all()
    for sep in seps:
        db.session.delete(sep)
    db.session.commit()
    return redirect(url_for('show_seps'))
