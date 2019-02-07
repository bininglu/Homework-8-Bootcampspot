import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, desc

from flask import Flask, jsonify
import datetime
# from datetime import datetime

#################################################
# Database Setup
#################################################
engine = create_engine('sqlite://///Users/bininglu/Desktop/Activities/Class activity/Module 10 activity/Homework/Instructions/Resources/hawaii.sqlite')


# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
# conn = engine.connect()
# session = Session (bind = conn)
session = Session(engine)
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
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Convert the query results to a Dictionary using `date` as the key and `prcp` as the value."""
    # Query all measurement data
    dates = session.query(Measurement.date).all()
    prcps = session.query(Measurement.prcp).all()
    all_date = list(np.ravel(dates))
    all_prcp = list(np.ravel(prcps))
    prcp_dict = {}
    prcp_dict = dict(zip(all_date, all_prcp))
    return jsonify(prcp_dict)
    
@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations from the dataset."""
    # Query all station data
    station_results = session.query(Station).all()
    all_stations = []
    for entry in station_results:
        station_dict = {}
        station_dict["station"] = entry.station
        station_dict["name"] = entry.name
        station_dict["latitude"] = entry.latitude
        station_dict["longitude"] = entry.longitude
        station_dict["elevation"] = entry.elevation
        all_stations.append(station_dict)
    return jsonify(all_stations)


@app.route("/api/v1.0/tobs")
def tobs():
    """query for the dates and temperature observations from a year from the last data point."""
    """Return a JSON list of Temperature Observations (tobs) for the previous year."""
    all_prcp = session.query(Measurement).order_by(desc(Measurement.date)).limit(1)
    for prcp in all_prcp:
        last_date=prcp.date

    parsed_prev_year=datetime.datetime.strptime(last_date, "%Y-%m-%d").date()- datetime.timedelta(days=365)
    formatted_prev_year = parsed_prev_year.strftime("%Y-%m-%d")
    # return formatted_prev_year

    prev_year_date=session.query(Measurement.date).\
                    filter(Measurement.date>=formatted_prev_year).\
                    filter(Measurement.date<=last_date).all()
    prev_year_tob=session.query(Measurement.tobs).\
                    filter(Measurement.date>=formatted_prev_year).\
                    filter(Measurement.date<=last_date).all()

    prev_year_dates = list(np.ravel(prev_year_date))
    prev_year_tobs = list(np.ravel(prev_year_tob))
    tobs_dict = {}
    tobs_dict = dict(zip(prev_year_dates, prev_year_tobs))

    return jsonify(tobs_dict)



@app.route("/api/v1.0/<start>")
def startdate(start):
    """Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range."""
    """When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date."""
    
    start_date = datetime.datetime.strptime(start, "%Y-%m-%d").date()
    formatted_start_date = start_date.strftime("%Y-%m-%d")
    
    start_range_tmin_query=session.query(func.min(Measurement.tobs)).\
                    filter(Measurement.date>=formatted_start_date).all()
    start_range_tmax_query=session.query(func.max(Measurement.tobs)).\
                    filter(Measurement.date>=formatted_start_date).all()
    start_range_tavg_query=session.query(func.avg(Measurement.tobs)).\
                    filter(Measurement.date>=formatted_start_date).all()


    start_range_tmin = list(np.ravel(start_range_tmin_query))
    start_range_tmax = list(np.ravel(start_range_tmax_query))
    start_range_tavg = list(np.ravel(start_range_tavg_query))
    
    start_range_dict = {}
    start_range_dict = dict(minimum_temperature=start_range_tmin,
                        average_temperature=start_range_tavg,
                        maximum_temperature=start_range_tmax,
                        )
    return jsonify(start_range_dict)


@app.route("/api/v1.0/<start>/<end>")
def rangedate(start,end):
    """Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range."""
    """When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` for dates between the start and end date inclusive."""
    
    start_date = datetime.datetime.strptime(start, "%Y-%m-%d").date()
    formatted_start_date = start_date.strftime("%Y-%m-%d")
    end_date = datetime.datetime.strptime(end, "%Y-%m-%d").date()
    formatted_end_date = end_date.strftime("%Y-%m-%d")
    
    range_tmin_query=session.query(func.min(Measurement.tobs)).\
                    filter(Measurement.date>=formatted_start_date).\
                    filter(Measurement.date<=formatted_end_date).all()
    range_tmax_query=session.query(func.max(Measurement.tobs)).\
                    filter(Measurement.date>=formatted_start_date).\
                    filter(Measurement.date<=formatted_end_date).all()
    range_tavg_query=session.query(func.avg(Measurement.tobs)).\
                    filter(Measurement.date>=formatted_start_date).\
                    filter(Measurement.date<=formatted_end_date).all()


    range_tmin = list(np.ravel(range_tmin_query))
    range_tmax = list(np.ravel(range_tmax_query))
    range_tavg = list(np.ravel(range_tavg_query))
    
    range_dict = {}
    range_dict = dict(minimum_temperature=range_tmin,
                        average_temperature=range_tavg,
                        maximum_temperature=range_tmax,
                        )
    return jsonify(range_dict)


if __name__ == "__main__":
    app.run(debug=True)
