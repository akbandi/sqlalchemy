import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)


# Create an app, being sure to pass __name__
app = Flask(__name__)

# Define what to do when a user hits the index route
@app.route("/")
def home():
    """Homepage."""
    """List all available api routes."""
    return (
    f"/api/v1.0/precipitation<br/>"
    f"/api/v1.0/stations<br/>"
    f"/api/v1.0/tobs<br/>"
    f"/api/v1.0/&lt;start&gt;<br/>"
    f"/api/v1.0/&lt;start&gt;/&lt;end&gt;"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return a list of all prcp names"""
    # Query all prcp
    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= '2016-08-23').\
        group_by(Measurement.date).all()
    
    session.close()

    all_precipitation = []

    # Query for the dates and temperature observations from the last year.
    for result in results:
        precipitation_dict = {}
        precipitation_dict["date"] = result[0]
        precipitation_dict["prcp"] = result[1]
        all_precipitation.append(precipitation_dict)
    return jsonify(all_precipitation)


@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations from the dataset."""
    # Return a list of active weather stations in Hawaii
    sel = [Measurement.station]
    active_stations = session.query(*sel).\
        group_by(Measurement.station).all()
    session.close()

    # Convert list of tuples into normal list and return the JSonified list
    list_of_stations = list(np.ravel(active_stations)) 
    return jsonify(list_of_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    """Return a JSON list of temperature observations (TOBS) for the previous year."""
    # Query the last 12 months of temperature observation data for the most active station
    sel = [Measurement.date, 
        Measurement.tobs]
    station_temps = session.query(*sel).\
            filter(Measurement.date >= '2016-08-23', Measurement.station == 'USC00519281').\
            group_by(Measurement.date).\
            order_by(Measurement.date).all()
        
    session.close()

    # Return a dictionary with the date as key and the daily temperature observation as value
    observation_dates = []
    temperature_observations = []

    for date, observation in station_temps:
        observation_dates.append(date)
        temperature_observations.append(observation)
    
    most_active_tobs_dict = dict(zip(observation_dates, temperature_observations))

    return jsonify(most_active_tobs_dict)

@app.route("/api/v1.0/<start>")
def temp(start='2016-08-23'):
    """Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a given start date."""

    results = session.query(func.min(Measurement.tobs).label('min'), \
        func.avg(Measurement.tobs).label('avg'), func.max(Measurement.tobs).label('max')). \
        filter(Measurement.date >= start).all()

    session.close()

    temp_data = []
    for r in results:
        temp = {}
        temp['Start Date'] = start
        temp['Min Temp'] = r.min
        temp['Avg Temp'] = r.avg
        temp['Max Temp'] = r.max
        temp_data.append(temp)

        return jsonify(temp_data)

@app.route("/api/v1.0/<start>/<end>")
def temp_start_end(start='2016-08-23', end='2017-08-23'):
    """Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a given start-end range."""
    
    results = session.query(func.min(Measurement.tobs).label('min'), \
        func.avg(Measurement.tobs).label('avg'), func.max(Measurement.tobs).label('max')). \
        filter(Measurement.date >= start). \
        filter(Measurement.date <= end).all()

    session.close()

    temp_start_end_data = []
    for r in results:
        temp_start_end = {}
        temp_start_end['Start Date'] = start
        temp_start_end['Min Temp'] = r.min
        temp_start_end['Avg Temp'] = r.avg
        temp_start_end['Max Temp'] = r.max
        temp_start_end['End Date'] = end
        temp_start_end_data.append(temp_start_end)

        return jsonify(temp_start_end_data)


if __name__ == "__main__":
    app.run(debug=True)
