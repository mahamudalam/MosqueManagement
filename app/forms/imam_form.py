from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SubmitField
from wtforms.validators import DataRequired


class ImamForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    mobile = StringField("Mobile")
    address = StringField("Address")
    monthly_salary = FloatField("Monthly Salary")
    submit = SubmitField("Save")
