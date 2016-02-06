from flask.ext.wtf import Form
from wtforms import StringField,BooleanField,PasswordField,DateField,FloatField,FileField
from wtforms.validators import DataRequired

class StartTripForm(Form):
    trip_type = StringField('Naam toh bata',validators=[DataRequired()])
    trip_friends = StringField('phone number de re baba',validators=[DataRequired()])
    vehicle= StringField('Enter your gmail username',validators=[DataRequired()])
    start_location= StringField('Password please',validators=[DataRequired()])
    start_timestamp=StringField('',validators=[DataRequired()])

class EndTripForm(Form):
    end_timestamp = StringField('Naam toh bata',validators=[DataRequired()])
    privacy = BooleanField('phone number de re baba')
    rating= StringField('Enter your gmail username',validators=[DataRequired()])
    end_location= StringField('Password please',validators=[DataRequired()])


class PitStopForm(Form):
    pass
