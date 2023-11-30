# Import the dependencies.
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import numpy as np
import pandas as pd
import datetime as dt
from datetime import datetime, timedelta
from pandas import DataFrame

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save reference to the table
Measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all passenger names"""
    # Query all passengers
    query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= query_date).all()

    session.close()

    # Create a dictionary from the row data and append to a list of all_passengers
    precip_data = []
    for date,prcp in results:
        precip_dict = {}
        precip_dict["Date"] = date
        precip_dict["Precipitation"] = prcp
        precip_data.append(precip_dict)

    return jsonify(precip_data)


@app.route("/api/v1.0/stations")
def stations():

    # Create our session (link) from Python to the DB
    session = Session(engine)

    results = session.query(Measurement.station).all()

    session.close()

    all_names = list(np.ravel(results))

    return jsonify(all_names)

@app.route("/api/v1.0/tobs")
def tobs():

    # Create our session (link) from Python to the DB
    session = Session(engine)

    query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    most_active_station_id = 'USC00519281'

    results = session.query(Measurement.date, Measurement.tobs) \
    .filter(Measurement.station == most_active_station_id) \
    .filter(Measurement.date >= query_date) \
    .all()

    session.close()

    all_names = list(np.ravel(results))

    return jsonify(all_names)

@app.route("/api/v1.0/<start>")
def temperature_stats_start(start):
    # Convert the start date string to a datetime object
    start_date = dt.datetime.strptime(start, "%Y-%m-%d")

    # Query to get TMIN, TAVG, and TMAX for dates greater than or equal to the start date
    results = session.query(func.min(Measurement.tobs).label("TMIN"),
                            func.avg(Measurement.tobs).label("TAVG"),
                            func.max(Measurement.tobs).label("TMAX")).\
        filter(Measurement.date >= start_date).all()

    # Convert the results to a dictionary
    temperature_stats = {
        "TMIN": results[0][0],
        "TAVG": results[0][1],
        "TMAX": results[0][2]
    }

    return jsonify(temperature_stats)

@app.route("/api/v1.0/<start>/<end>")
def temperature_stats_range(start, end):
    # Convert the start and end date strings to datetime objects
    start_date = dt.datetime.strptime(start, "%Y-%m-%d")
    end_date = dt.datetime.strptime(end, "%Y-%m-%d")

    # Query to get TMIN, TAVG, and TMAX for dates within the specified range
    results = session.query(func.min(Measurement.tobs).label("TMIN"),
                            func.avg(Measurement.tobs).label("TAVG"),
                            func.max(Measurement.tobs).label("TMAX")).\
        filter(and_(Measurement.date >= start_date, Measurement.date <= end_date)).all()

    # Convert the results to a dictionary
    temperature_stats = {
        "TMIN": results[0][0],
        "TAVG": results[0][1],
        "TMAX": results[0][2]
    }

    return jsonify(temperature_stats)


#################################################
# Flask Routes
#################################################
if __name__ == '__main__':
    app.run(debug=True)