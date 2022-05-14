from wtforms import Form, StringField
from wtforms.validators import InputRequired


class Command(Form):
    comm = StringField('Command:', validators=[InputRequired()])
