"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import render_template
from DemoFormProject import app
from DemoFormProject.Models.LocalDatabaseRoutines import create_LocalDatabaseServiceRoutines

from datetime import datetime
from flask import render_template, redirect, request

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

from mpl_toolkits.mplot3d import Axes3D

from matplotlib.figure import Figure
from DemoFormProject.Models.plot_service_functions import plot_to_img

from geopy import Nominatim

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

import json 
import requests

import io
import base64

from os import path

from flask   import Flask, render_template, flash, request
from wtforms import Form, BooleanField, StringField, PasswordField, validators
from wtforms import TextField, TextAreaField, SubmitField, SelectField, DateField
from wtforms import ValidationError


from DemoFormProject.Models.QueryFormStructure import QueryFormStructure 
from DemoFormProject.Models.QueryFormStructure import LoginFormStructure 
from DemoFormProject.Models.QueryFormStructure import UserRegistrationFormStructure 

from DemoFormProject.Models.Forms import ExpandForm
from DemoFormProject.Models.Forms import CollapseForm
from flask_bootstrap import Bootstrap
bootstrap = Bootstrap(app)
app.config['SECRET_KEY'] = 'The first argument to the field'

db_Functions = create_LocalDatabaseServiceRoutines() 

@app.route('/')
@app.route('/home')
def home():
    """Renders the home page."""
    return render_template(
        'index.html',
        title='Home Page',
        year=datetime.now().year,
        new_york_pic='/static/Pics/newYorkPic.png'
    )

@app.route('/contact')
def contact():
    """Renders the contact page."""
    return render_template(
        'contact.html',
        title='Contact',
        year=datetime.now().year,
        message='Email, phone number and address:'

    )

@app.route('/about')
def about():
    """Renders the about page."""
    return render_template(
        'about.html',
        year=datetime.now().year,
        message='About the project',
        tichonet_image = '/static/Pics/tichonet.png'
    )


@app.route('/Album')
def Album():
    """Renders the about page."""
    return render_template(
        'PictureAlbum.html',
        title='Picture Album',
        year=datetime.now().year,
        message='Here are some pictures of NYC:'
    )


@app.route('/Query', methods=['GET', 'POST'])
def Query():
    geolocator = Nominatim(user_agent="final data science project")

    airbnbMap = 'static/pics/airbnbMap.PNG'
    crimeMap = 'static/pics/crimeRatesMap.PNG'
    partyMap = 'static/pics/partyMap.PNG'

    Name = None
    Country = ''
    capital = ''
    dr = pd.read_csv(path.join(path.dirname(__file__), 'static\\Data\\nyc-rolling-sales.csv'))
    rollingSalesAdresses = dr['ADDRESS']

    def findLongLat(address):
        adress = geolocator.geocode(address)
        return [adress.latitude, adress.longitude]

    def removeComma(string):
        if string.find(',') < 0:
            return string
        else:
            return string[0:string.find(',')]

    def findRollingSales(address):
        numSales = 0
        for x in range(0, rollingSalesAdresses.size):
            if removeComma(str(rollingSalesAdresses[x])).replace(' ', '').lower() == address.replace(' ', '').lower():
                numSales = numSales + 1
        return numSales

    raw_data_table = dr.to_html(classes = 'table table-hover', max_rows=10, max_cols=5)

    form = QueryFormStructure(request.form)

    
     #_________________________________________
    if (request.method == 'POST' ):
        name = form.name.data
        Country = name
        if (findRollingSales(name) > 0):
            capital = str(findRollingSales(name))
            raw_data_table = ""
        else:
            capital = str(findRollingSales(name))
        form.name.data = ''

        ydata = findLongLat(name+ " NYC")[1]
        xdata = findLongLat(name + " NYC")[0]

        airbnbMap = plt.imread(path.join(path.dirname(__file__), airbnbMap))

        fig7 = plt.figure()
        qAirbnb = fig7.add_subplot(111)
        qAirbnb.imshow(airbnbMap, extent=[40.499790000000004, 40.913059999999994, -74.24441999999999, -73.71299])
        qAirbnb.scatter(xdata, ydata, 10,color='red')
        airbnbMap = plot_to_img(fig7)

        crimeMap = plt.imread(path.join(path.dirname(__file__), crimeMap))

        fig8 = plt.figure()
        qCrime = fig8.add_subplot(111)
        qCrime.imshow(crimeMap, extent=[40.499790000000004, 40.913059999999994, -74.24441999999999, -73.71299])
        qCrime.scatter(xdata, ydata, 10,color='red')
        crimeMap = plot_to_img(fig8)

        partyMap = plt.imread(path.join(path.dirname(__file__), partyMap))

        fig9 = plt.figure()
        qParty = fig9.add_subplot(111)
        qParty.imshow(partyMap, extent=[40.499790000000004, 40.913059999999994, -74.24441999999999, -73.71299])
        qParty.scatter(xdata, ydata, 10,color='red')
        partyMap = plot_to_img(fig9)



    return render_template('Query.html', 
            qAirbnb = airbnbMap,
            qCrime = crimeMap,
            qParty = partyMap,
            form = form, 
            name = capital, 
            Country = Country,
            raw_data_table = raw_data_table,
            title='Query:',
            year=datetime.now().year,
            message='Type in an address in new york to see how many rolling sales were in that address during 2016 and the long and lat coordinates'
        )

# -------------------------------------------------------
# Register new user page
# -------------------------------------------------------
@app.route('/register', methods=['GET', 'POST'])
def Register():
    form = UserRegistrationFormStructure(request.form)

    if (request.method == 'POST' and form.validate()):
        if (not db_Functions.IsUserExist(form.username.data)):
            db_Functions.AddNewUser(form)
            db_table = ""

            flash('Thanks for registering new user - '+ form.FirstName.data + " " + form.LastName.data )
            # Here you should put what to do (or were to go) if registration was good
        else:
            flash('Error: User with this Username already exist ! - '+ form.username.data)
            form = UserRegistrationFormStructure(request.form)

    return render_template(
        'register.html', 
        form=form, 
        title='Register New User',
        year=datetime.now().year,
        repository_name='Pandas',
        )

# -------------------------------------------------------
# Login page
# This page is the filter before the data analysis
# -------------------------------------------------------
@app.route('/login', methods=['GET', 'POST'])
def Login():
    form = LoginFormStructure(request.form)

    if (request.method == 'POST' and form.validate()):
        if (db_Functions.IsLoginGood(form.username.data, form.password.data)):
            flash('Login approved!')
            return redirect('DataModel')
        else:
            flash('Error in - Username and/or password')
   
    return render_template(
        'login.html', 
        form=form, 
        title='Login to data analysis',
        year=datetime.now().year,
        repository_name='Pandas',
        )

@app.route('/DataSet1', methods=['GET', 'POST'])
def DataSet1():

    """Renders the contact page."""
    form1 = ExpandForm()
    form2 = CollapseForm()
    df = pd.read_csv(path.join(path.dirname(__file__), 'static/Data/AB_NYC_2019.csv'))
    raw_data_table = ''
    if request.method == 'POST':
        if request.form['action'] == 'Expand' and form1.validate_on_submit():
                raw_data_table = df.to_html(classes = 'table table-hover', max_rows=50, max_cols=20)
        if request.form['action'] == 'Collapse' and form2.validate_on_submit():
            raw_data_table = ''
            #raw_data_table = df.to_html(classes = 'table table-hover')


    return render_template(
            'DataSet1.html',
            title='Airbnb sales',
            year=datetime.now().year,
            message='This dataset contains NYC airbnb sales throughout 2015-2016',
            raw_data_table = raw_data_table,
    	    form1 = form1,
    	    form2 = form2

        )

@app.route('/DataSet2', methods=['GET', 'POST'])
def DataSet2():

    """Renders the contact page."""
    form1 = ExpandForm()
    form2 = CollapseForm()
    df = pd.read_csv(path.join(path.dirname(__file__), 'static/Data/nyc-rolling-sales.csv'))
    raw_data_table = ''
    if request.method == 'POST':
        if request.form['action'] == 'Expand' and form1.validate_on_submit():
                raw_data_table = df.to_html(classes = 'table table-hover', max_rows=50, max_cols=20)
        if request.form['action'] == 'Collapse' and form2.validate_on_submit():
            raw_data_table = ''
            #raw_data_table = df.to_html(classes = 'table table-hover')


    return render_template(
            'DataSet1.html',
            title='NYC rolling sales',
            year=datetime.now().year,
            message='This dataset contains NYC rolling sales throughout 2015-2016',
            raw_data_table = raw_data_table,
    	    form1 = form1,
    	    form2 = form2

        )

@app.route('/DataSet3', methods=['GET', 'POST'])
def DataSet3():

    """Renders the contact page."""
    form1 = ExpandForm()
    form2 = CollapseForm()
    df = pd.read_csv(path.join(path.dirname(__file__), 'static/Data/NYPD_Complaint_Data_Historic.csv'))
    raw_data_table = ''
    if request.method == 'POST':
        if request.form['action'] == 'Expand' and form1.validate_on_submit():
                raw_data_table = df.to_html(classes = 'table table-hover', max_rows=50, max_cols=20)
        if request.form['action'] == 'Collapse' and form2.validate_on_submit():
            raw_data_table = ''
            #raw_data_table = df.to_html(classes = 'table table-hover')


    return render_template(
            'DataSet1.html',
            title='Crime reports',
            year=datetime.now().year,
            message='This dataset contains crime reports in NYC throughout 2015-2016',
            raw_data_table = raw_data_table,
    	    form1 = form1,
    	    form2 = form2

        )

@app.route('/DataSet4', methods=['GET', 'POST'])
def DataSet4():

    """Renders the contact page."""
    form1 = ExpandForm()
    form2 = CollapseForm()
    df = pd.read_csv(path.join(path.dirname(__file__), 'static/Data/party_in_nyc.csv'))
    raw_data_table = ''
    if request.method == 'POST':
        if request.form['action'] == 'Expand' and form1.validate_on_submit():
                raw_data_table = df.to_html(classes = 'table table-hover', max_rows=50, max_cols=20)
        if request.form['action'] == 'Collapse' and form2.validate_on_submit():
            raw_data_table = ''
            #raw_data_table = df.to_html(classes = 'table table-hover')


    return render_template(
            'DataSet1.html',
            title='Party complaints',
            year=datetime.now().year,
            message='This dataset contains party complaints in NYC throughotu 2015-2016',
            raw_data_table = raw_data_table,
    	    form1 = form1,
    	    form2 = form2

        )

@app.route('/DataModel', methods = ['GET' , 'POST'])
def DataModel():

    ds = pd.read_csv(path.join(path.dirname(__file__), 'static/Data/AB_NYC_2019.csv'))
    newYorkMap = plt.imread(path.join(path.dirname(__file__), 'static/Pics/newYorkMap.PNG'))

    ydata = ds['longitude']
    xdata = ds['latitude']

    fig = plt.figure()
    twoAirbnb = fig.add_subplot(111)
    twoAirbnb.imshow(newYorkMap, extent=[40.499790000000004, 40.913059999999994, -74.24441999999999, -73.71299])
    twoAirbnb.scatter(xdata, ydata, 1)

    twoAirbnbImage = plot_to_img(fig)

    #_____________________________________________________________________________________________________________



    def getAirbnbsInLongLat(longMax, longMin, latMax, latMin):
        dsGreaterThanLong = ds[ds['longitude'] >= longMin]
        dsLessThanLong = dsGreaterThanLong[dsGreaterThanLong['longitude'] < longMax]
        dsGreaterThanLat = dsLessThanLong[dsLessThanLong['latitude'] >= latMin]
        return dsGreaterThanLat[dsGreaterThanLat['latitude'] < latMax].size

    def returnBarGraphMatrixAirbnb(barsX, barsY):
        barGraphMatrixAirbnb = [0] * (barsY * barsX)
        for x in range(0, barsX):
            for y in range(0, barsY):
                barGraphMatrixAirbnb[(x * barsX) + y] = getAirbnbsInLongLat(-74.24441999999999 + (0.5314299999999861 / barsY) * (y + 1), -74.24441999999999 + (0.5314299999999861 / barsY) * y, 40.499790000000004 + (0.41326999999999003 / barsX) * (x + 1), 40.499790000000004 + (0.41326999999999003 / barsX) * x)
        return barGraphMatrixAirbnb

    numLatBars = 6
    numLongBars = 6
    xdataThree = [0] * (numLatBars * numLongBars)
    ydataThree = [0] * (numLatBars * numLongBars)

    for a in range(0, numLatBars):
        for b in range(0, numLongBars):
            ydataThree[(a * numLatBars) + b] = -74.24441999999999 + (0.5314299999999861 / numLongBars) * b

    for c in range(0, numLongBars):
        for d in range(0, numLatBars):
            xdataThree[(c * numLongBars) + d] = 40.499790000000004 + (0.41326999999999003 / numLatBars) * c

    fig2 = plt.figure()
    threeAribnb = fig2.add_subplot(111, projection='3d')
    zdata = returnBarGraphMatrixAirbnb(numLatBars, numLongBars) 
    threeAribnb.bar3d(xdataThree, ydataThree, 0, (0.41326999999999003 / numLatBars) / 2, (0.5314299999999861 / numLongBars) / 2, zdata, 'blue', shade= True)

    threeAirbnbImage = plot_to_img(fig2)

    #______________________________________________________________________________________________________________________________________

    dl = pd.read_csv(path.join(path.dirname(__file__), 'static/Data/NYPD_Complaint_Data_Historic.csv'))

    ydata = dl['Longitude']
    xdata = dl['Latitude']

    fig3 = plt.figure()
    twoCrime = fig3.add_subplot(111)

    twoCrime.imshow(newYorkMap, extent=[40.499790000000004, 40.913059999999994, -74.24441999999999, -73.71299])
    twoCrime.scatter(xdata, ydata, 1)

    twoCrimeImage = plot_to_img(fig3)

    #______________________________________________________________________________________________________________________________________

    def getCrimesInLongLat(longMax, longMin, latMax, latMin):
        dlGreaterThanLong = dl[dl['Longitude'] >= longMin]
        dlLessThanLong = dlGreaterThanLong[dlGreaterThanLong['Longitude'] < longMax]
        dlGreaterThanLat = dlLessThanLong[dlLessThanLong['Latitude'] >= latMin]
        return dlGreaterThanLat[dlGreaterThanLat['Latitude'] < latMax].size

    def returnBarGraphMatrixCrime(barsX, barsY):
        barGraphMatrixCrime = [0] * (barsY * barsX)
        for x in range(0, barsX):
            for y in range(0, barsY):
                barGraphMatrixCrime[(x * barsX) + y] = getCrimesInLongLat(-74.25507554 + (0.5544990300000023 / barsY) * (y + 1), -74.25507554 + (0.5544990300000023 / barsY) * y, 40.49876753 + (0.41395586999999523 / barsX) * (x + 1), 40.49876753 + (0.41395586999999523 / barsX) * x)
        return barGraphMatrixCrime

    numLatBars = 6
    numLongBars = 6
    xdataThree = [0] * (numLatBars * numLongBars)
    ydataThree = [0] * (numLatBars * numLongBars)
    for a in range(0, numLatBars):
        for b in range(0, numLongBars):
            ydataThree[(a * numLatBars) + b] = -74.25507554 + (0.5544990300000023 / numLongBars) * b
    for c in range(0, numLongBars):
        for d in range(0, numLatBars):
            xdataThree[(c * numLongBars) + d] = 40.49876753 + (0.41395586999999523 / numLatBars) * c  
            
    zdata = returnBarGraphMatrixCrime(numLatBars, numLongBars) 

    fig4 = plt.figure()
    threeCrime = fig4.add_subplot(111, projection = '3d')
    threeCrime.bar3d(xdataThree, ydataThree, 0, (0.41395586999999523 / numLatBars) / 2, (0.5544990300000023 / numLongBars) / 2, zdata, 'blue', shade= True)

    threeCrimeImage = plot_to_img(fig4)

    #___________________________________________________________________________________________________________________________________________

    dt = pd.read_csv(path.join(path.dirname(__file__), 'static/Data/party_in_nyc.csv'))

    ydata = dt['Longitude']
    xdata = dt['Latitude']

    fig5 = plt.figure()
    twoParty = fig5.add_subplot(111)
    twoParty.imshow(newYorkMap, extent=[40.499790000000004, 40.913059999999994, -74.24441999999999, -73.71299])
    twoParty.scatter(xdata, ydata, 1)

    twoPartyImage = plot_to_img(fig5)

    #____________________________________________________________________________________________________________________________________________

    def getPartiesInLongLat(longMax, longMin, latMax, latMin):
        dtGreaterThanLong = dt[dt['Longitude'] >= longMin]
        dtLessThanLong = dtGreaterThanLong[dtGreaterThanLong['Longitude'] < longMax]
        dtGreaterThanLat = dtLessThanLong[dtLessThanLong['Latitude'] >= latMin]
        return dtGreaterThanLat[dtGreaterThanLat['Latitude'] < latMax].size

    def returnBarGraphMatrixParty(barsX, barsY):
        barGraphMatrixParty = [0] * (barsY * barsX)
        for x in range(0, barsX):
            for y in range(0, barsY):
                barGraphMatrixParty[(x * barsX) + y] = getPartiesInLongLat(-74.25507554 + (0.5544990300000023 / barsY) * (y + 1), -74.25507554 + (0.5544990300000023 / barsY) * y, 40.49876753 + (0.41395586999999523 / barsX) * (x + 1), 40.49876753 + (0.41395586999999523 / barsX) * x)
        return barGraphMatrixParty

    numLatBars = 6
    numLongBars = 6
    xdataThree = [0] * (numLatBars * numLongBars)
    ydataThree = [0] * (numLatBars * numLongBars)
    for a in range(0, numLatBars):
        for b in range(0, numLongBars):
            ydataThree[(a * numLatBars) + b] = -74.25127710072611 + (0.5489745351470532 / numLongBars) * b
    for c in range(0, numLongBars):
        for d in range(0, numLatBars):
            xdataThree[(c * numLongBars) + d] = 40.498819681472185 + (0.4133587216089438 / numLatBars) * c
        
    zdata = returnBarGraphMatrixParty(numLatBars, numLongBars) 

    fig6 = plt.figure()
    threeParty = fig6.add_subplot(111, projection='3d')
    threeParty.bar3d(xdataThree, ydataThree, 0, (0.4133587216089438 / numLatBars) / 2, (0.5489745351470532 / numLongBars) / 2, zdata, 'blue', shade= True)

    threePartyImage = plot_to_img(fig6)

    return render_template(

            'DataModel.html',
            twoAirbnb = twoAirbnbImage,
            threeAirbnb = threeAirbnbImage,
            twoCrime = twoCrimeImage,
            threeCrime = threeCrimeImage,
            twoParty = twoPartyImage,
            threeParty = threePartyImage,
            title='This is my Data Model page',
            year=datetime.now().year,
            message='In this page we will display the datasets i used to show you where have the Virus spread to',

        )

@app.route('/toData')
def NewPage():
    """Renders the NewPage page."""
    return render_template(
        'toDataSet.html',
        year=datetime.now().year
    )


