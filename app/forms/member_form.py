from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SubmitField
from wtforms.validators import DataRequired


class MemberForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    phone = StringField("Phone")
    address = StringField("Address")
    imam_salary_contri = FloatField("Imam Salary Contribution")
    submit = SubmitField("Save")
