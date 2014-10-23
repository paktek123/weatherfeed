import os
import json
from flask import Flask, request
from flask_wtf import Form
from wtforms import IntegerField
from wtforms.validators import DataRequired
from flask.ext.sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.debug = True
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
    self.data = dict(lightning=self.lightning, rain=self.rain, wind=self.wind, cloud=self.cloud)
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

@app.route('/consume', methods=('POST',))
def consume():
  form = WeatherForm(request.form, csrf_enabled=False)
  if form.validate_on_submit():
    weather = Weather(form.lightning.data, form.rain.data, form.wind.data, form.cloud.data)
    db.session.add(weather)
    db.session.commit()

    # run some maintanence
    all_weather = Weather.query.all()
    if len(all_weather) > 90000:
      db.session.delete(all_weather[0])
      db.session.commit()

    db.session.remove()
    return json.dumps('SUCCESS'), 200
  else:
    return json.dumps(form.errors), 401

@app.route('/now')
def show_data():
  all_weather = Weather.query.all()
  return json.dumps([dict(lightning=w.lightning, rain=w.rain, wind=w.wind, cloud=w.cloud) for w in all_weather][-1])

@app.route('/forecast')
def forecast():
  all_weather = Weather.query.all()
  todays_data = [w for w in all_weather if w.created_at.day == datetime.now().day and w.created_at.month == datetime.now().month]
  if not todays_data:
    todays_data = all_weather[-7:]
  agg_lightning = sum(w.lightning for w in todays_data) / len(todays_data)
  agg_rain = sum(w.rain for w in todays_data) / len(todays_data)
  agg_wind = sum(w.wind for w in todays_data) / len(todays_data)
  agg_cloud = sum(w.cloud for w in todays_data) / len(todays_data)
  return json.dumps(dict(lightning=agg_lightning, rain=agg_rain, wind=agg_wind, cloud=agg_cloud))


if __name__ == '__main__':
  app.run(debug=True)
