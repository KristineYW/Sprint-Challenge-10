"""OpenAQ Air Quality Dashboard with Flask."""
from flask_sqlalchemy import SQLAlchemy
# from flask_migrate import Migrate
from flask import Flask
import openaq

APP = Flask(__name__)

APP.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'

DB = SQLAlchemy(APP)

api = openaq.OpenAQ()


# DB.init_app(APP)
# Migrate.init_app(APP, DB)

class Record(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    datetime = DB.Column(DB.String(25))
    value = DB.Column(DB.Float, nullable=False)

    def __repr__(self):
        return f"<Air Quality Check Info: {self.id} {self.datetime} {self.value}>"

def get_results(city='Los Angeles', parameter='pm25'):
    status, body = api.measurements(city='Los Angeles', parameter='pm25')

    utc_datetimes = []
    for i in range(0, 100):
        utc = body['results'][i]['date']['utc']
        utc_datetimes.append(utc)

    values = []
    for j in range(0, 100):
        value = body['results'][j]['value']
        values.append(value)

    return utc_datetimes, values


@APP.route('/')
def root():
    utc_datetimes, values = get_results()
    return ("The values are " + str(values) + " and the UTC datetimes are " + str(utc_datetimes))


@APP.route('/refresh')
def refresh():
    """Pull fresh data from Open AQ and replace existing data."""
    DB.drop_all()
    DB.create_all()

    new_utc, new_values = get_results(city='Los Angeles', parameter='pm25')
    new_record = list(zip(new_utc, new_values))
    for i in new_record:
        new_db = Record(datetime=i[0], value=i[1])
        DB.session.add(new_db)

    DB.session.commit()
    return "Data refreshed!"
