import os
import json
import requests
from flask import Flask, request
from flask_wtf import Form
from wtforms import IntegerField
from wtforms.validators import DataRequired
from flask.ext.sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
db = SQLAlchemy(app)

class Weather(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  lightning = db.Column(db.Integer)
  rain = db.Column(db.Integer)
  wind = db.Column(db.Integer)
  cloud = db.Column(db.Integer)
  created_at = db.Column(db.DateTime, default=datetime.now())

  def __init__(self, lightning, rain, wind, cloud, created_at=None):
    self.lightning = lightning
    self.rain = rain
    self.wind = wind
    self.cloud = cloud
    self.created_at = created_at
    if not self.created_at:
      self.created_at = datetime.now()

  def __repr__(self):
    return '<%s>' % self.id

class WeatherForm(Form):
  lightning = IntegerField('lightning', validators=[DataRequired()])
  rain = IntegerField('rain', validators=[DataRequired()])
  wind = IntegerField('wind', validators=[DataRequired()])
  cloud = IntegerField('cloud', validators=[DataRequired()])

@app.route('/consume', methods=('POST'))
def consume():
  form = WeatherForm(request.form)
  if form.validate_on_submit():
    weather = Weather(form.lightning.data, form.rain.data, form.wind.data, form.cloud.data)
    db.session.add(weather)
    db.session.commit()
    db.session.remove()
    return json.dumps('SUCCESS'), 200
  else:
    return json.dumps(form.errors), 401


@app.route('/now')
def show_data():
  data = {'':
    return 'Hello World!'
