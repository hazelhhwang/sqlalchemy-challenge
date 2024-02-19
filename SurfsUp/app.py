# Import the dependencies.
import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
from datetime import datetime

#################################################
# Database Setup
#################################################

# Create engine using the `hawaii.sqlite` database file
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Declare a Base using `automap_base()`
Base = automap_base()

# Use the Base class to reflect the database tables
Base.prepare(engine, reflect=True)

# Assign the measurement class to a variable called `Measurement` and
# the station class to a variable called `Station`
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create a session
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
        f"Welcome to the Climate App API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;" "(Replace &lt;start&gt; with the date format YYYY-MM-DD)<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;" "(Replace &lt;start&gt;/&lt;end&gt; with the date format YYYY-MM-DD)"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Convert the query results to a dictionary using date as the key and prcp as the value."""
    # Create a session
    session = Session(engine)
    
    # Query the last 12 months of precipitation data
    last_year_precipitation = session.query(Measurement.date, Measurement.prcp).\
                                filter(Measurement.date >= dt.date(2016, 8, 23)).all()

    # Close the session
    session.close()

    # Create a dictionary from the query results
    precipitation_data = {date: prcp for date, prcp in last_year_precipitation}
    
    return jsonify(precipitation_data)

@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations from the dataset."""
    # Create a session
    session = Session(engine)
    
    # Query all stations
    stations = session.query(Station.station).all()

    # Close the session
    session.close()

    # Convert list of tuples into normal list
    station_list = list(np.ravel(stations))
    
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    """Query the dates and temperature observations of the most-active station for the previous year of data."""
    # Create a session
    session = Session(engine)
    
    # Query the most active station
    most_active_station = session.query(Measurement.station).\
                            group_by(Measurement.station).\
                            order_by(func.count(Measurement.station).desc()).\
                            first()[0]

    # Query the last 12 months of temperature data for the most active station
    last_year_tobs = session.query(Measurement.date, Measurement.tobs).\
                        filter(Measurement.date >= dt.date(2016, 8, 23)).\
                        filter(Measurement.station == most_active_station).all()

    # Close the session
    session.close()

    # Create a dictionary from the query results
    tobs_data = {date: tobs for date, tobs in last_year_tobs}
    
    return jsonify(tobs_data)

@app.route("/api/v1.0/<start>")
def start_date(start):
    """Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start date."""
    # Create a session
    session = Session(engine)

    # Convert the start parameter to a datetime object
    start_date = datetime.strptime(start, '%Y-%m-%d')
    
    # Query temperatures greater than or equal to start date
    temp_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.date >= start_date).all()

    # Close the session
    session.close()

    # Convert list of tuples into a dictionary
    temp_dict = {
        "TMIN": temp_data[0][0],
        "TAVG": temp_data[0][1],
        "TMAX": temp_data[0][2]
    }
    
    return jsonify(temp_dict)

@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    """Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start and end date range."""
    # Create a session
    session = Session(engine)
    
    # Query temperatures between start and end dates
    temp_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    # Close the session
    session.close()

    # Convert list of tuples into a dictionary
    temp_dict = {
        "TMIN": temp_data[0][0],
        "TAVG": temp_data[0][1],
        "TMAX": temp_data[0][2]
    }
    
    return jsonify(temp_dict)

if __name__ == "__main__":
    app.run(debug=True)