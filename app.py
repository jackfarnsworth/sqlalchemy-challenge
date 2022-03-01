import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

# Save latest date in database
session = Session(engine)
latest_date = session.query(measurement.date).order_by(measurement.date.desc()).first()[0]
session.close()
#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )


@app.route("/api/v1.0/stations")
def names():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all passenger names"""
    # Query all passengers
    results = session.query(station.station).all()

    session.close()

    # Convert list of tuples into normal list
    all_names = list(np.ravel(results))

    return jsonify(all_names)


@app.route("/api/v1.0/precipitation")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query dates and prcp
    results = session.query(measurement.date, measurement.prcp).all()

    session.close()

    # Create a dictionary from the row data and append to a list of all_passengers
    prcp_dict = {}
    for date, prcp in results:
        prcp_dict[date] = prcp

    return prcp_dict

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    yearprior = dt.datetime.strptime(latest_date, '%Y-%m-%d') - dt.timedelta(days=365)
    max_station = session.query(measurement.station) \
                        .group_by(measurement.station) \
                        .order_by(func.count(measurement.station).desc()) \
                        .first()[0]
    data_tobs = session.query(measurement.tobs) \
                        .filter(measurement.date >= yearprior) \
                        .filter(measurement.station == max_station) \
                        .order_by(measurement.date.desc()) \
                        .all()
    session.close()
    data_list = []
    for data in data_tobs:
        data_list.append(data[0])
    return jsonify(data_list)

@app.route("/api/v1.0/<start>")
def starttemps(start):
    session = Session(engine)
    temps = session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)) \
        .filter(measurement.date >= start).first()
    temp_dict = {
        'TMIN' : temps[0],
        'TMAX' : temps[1],
        'TAVG' : temps[2],
    }
    return temp_dict

@app.route("/api/v1.0/<start>/<end>")
def startendtemps(start,end):
    session = Session(engine)
    temps = session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)) \
        .filter(measurement.date >= start) \
        .filter(measurement.date <= end).first()
    temp_dict = {
        'TMIN' : temps[0],
        'TMAX' : temps[1],
        'TAVG' : temps[2],
    }
    return temp_dict


if __name__ == '__main__':
    app.run(debug=True)
