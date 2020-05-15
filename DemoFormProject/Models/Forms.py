from datetime import datetime

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms import Form, BooleanField, PasswordField
from wtforms import TextField, TextAreaField, SelectField, DateField
from wtforms import validators, ValidationError

from wtforms.validators import DataRequired
from wtforms.validators import InputRequired



class ExpandForm(FlaskForm):
	submit1 = SubmitField('Expand')
	name="Expand"
	value="Expand"
class CollapseForm(FlaskForm):
	submit2 = SubmitField('Collapse')
	name="Collapse"
	value="Collapse"