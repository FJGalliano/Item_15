import datetime as dt
import numpy as np
import pandas as pd
import os

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify, render_template


#################################################
#################  Database Setup ###############
#################################################
engine = create_engine("sqlite:///belly_button_biodiversity.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Metadata = Base.classes.samples_metadata
OTU = Base.classes.otu
Sample = Base.classes.samples

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
##################  Flask Setup  ################
#################################################
app = Flask(__name__)

#################################################
# ###############  Flask Routes  ################
#################################################

@app.route("/")
def index():
        return render_template("index.html")


@app.route('/names')
def names():
    """Return a list of all sample names"""
    # Query all names
    results = session.query(Sample).statement
    df1 = pd.read_sql_query(results, session.bind)
    df1.set_index("otu_id",inplace=True)
    
    # Convert list of tuples into normal list

    return jsonify(list(df1.columns))


@app.route('/otu')
def otus():
    """Return a list of OTU descriptions"""
    # Query all names
    results = session.query(OTU.lowest_taxonomic_unit_found).all()

    # Convert list of tuples into normal list
    all_names = list(np.ravel(results))

    return jsonify(all_names)


@app.route('/metadata/<sample>')
def metadata(sample):
    """Return a json dictionary of metadata"""
    # Query all OTUs
    sel = [Metadata.AGE,Metadata.BBTYPE,Metadata.GENDER,Metadata.LOCATION,Metadata.SAMPLEID,Metadata.ETHNICITY]
    results = session.query(*sel).\
        filter(Metadata.SAMPLEID == sample[3:]).all()
    # Create a dictionary from the row data and append to a list of all_OTUs
    all_sample_metadata = {}
    for result in results:
        all_sample_metadata["AGE:"] = result[0]
        all_sample_metadata["BBTYPE:"] = result[1]
        all_sample_metadata["GENDER:"] = result[2]
        all_sample_metadata["LOCATION:"] = result[3]
        all_sample_metadata["SAMPLEID:"] = result[4]
        all_sample_metadata["ETHNICITY:"] = result[5]
    return jsonify(all_sample_metadata)

@app.route('/wfreq/<sample>')
def wfreq(sample):
    """ Returns an INTEGER value for weekly washing frequency"""
    # Query all frequencies
    sel2 = [Metadata.WFREQ]
    results = session.query(*sel2).\
        filter(Metadata.SAMPLEID == sample[3:]).all()
    # results = session.query(Metadata.wfreq).all()
    all_Sample_Wfreq = {}
    for result in results:
        all_Sample_Wfreq["WFREQ:"] = result[0]
    # Convert list of tuples into normal list
    
    return jsonify(all_Sample_Wfreq)

@app.route('/samples/<sample>')
def sample(sample):
    """ Returns a list of dictionaries of OTU_IDs and Sample_Values"""
    # Query all OTU_ID and Sample Value
    results3 = session.query(Sample).statement
    df2 = pd.read_sql_query(results3, session.bind)
    
    #Find sample, if not show error
    if sample not in df2.columns:
        return jsonify(f"Error! Sample: {sample} Not Found!"), 400
    
    #Sample values greater than 1
    df2 = df2[df2[sample] > 1]

    #Sort
    df2 = df2.sort_values(by=sample, ascending = 0)

    #Format data
    sample_data = [{
        "otu_ids" : df2[sample].index.values.tolist(),
        "sample_values" : df2[sample].values.tolist()
    }]

    return jsonify(sample_data)
    

if __name__ == '__main__':
    app.run(debug=True)    