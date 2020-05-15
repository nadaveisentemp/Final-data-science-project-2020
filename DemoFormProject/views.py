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

    Name = None
    Country = ''
    capital = ''
    df = pd.read_csv(path.join(path.dirname(__file__), 'static\\Data\\capitals.csv'))
    dr = pd.read_csv(path.join(path.dirname(__file__), 'static\\Data\\nyc-rolling-sales.csv'))
    df = df.set_index('Country')
    rollingSalesAdresses = dr['ADDRESS']
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
     
    if (request.method == 'POST' ):
        name = form.name.data
        Country = name
        if (findRollingSales(name) > 0):
            capital = str(findRollingSales(name))
            raw_data_table = ""
        else:
            capital = str(findRollingSales(name))
        form.name.data = ''

    return render_template('Query.html', 
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
            title='This is my Data Model page about the CoronaViruses',
            year=datetime.now().year,
            message='In this page we will display the datasets i used to show you where have the Virus spread to',
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
            title='This is my Data Model page about the CoronaViruses',
            year=datetime.now().year,
            message='In this page we will display the datasets i used to show you where have the Virus spread to',
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
            title='This is my Data Model page about the CoronaViruses',
            year=datetime.now().year,
            message='In this page we will display the datasets i used to show you where have the Virus spread to',
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
            title='This is my Data Model page about the CoronaViruses',
            year=datetime.now().year,
            message='In this page we will display the datasets i used to show you where have the Virus spread to',
            raw_data_table = raw_data_table,
    	    form1 = form1,
    	    form2 = form2

        )

@app.route('/DataModel', methods = ['GET' , 'POST'])
def DataModel():
    return render_template(
            'DataModel.html',
            title='This is my Data Model page about the CoronaViruses',
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


