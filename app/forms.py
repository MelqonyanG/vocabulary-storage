from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, RadioField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app.models import User

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class TestForm(FlaskForm):
    direct = RadioField('Direction', choices=[
            ('english', 'from english to armenian'),
            ('armenian', 'from armenian to english')
        ]
    )
    sort = RadioField('Sorted by', choices=[
            ('date','date'),
            ('alphabet','alphabet'),
            ('random', 'random')
        ]
    )
    submit = SubmitField('Start')

class AddNewWordsForm(FlaskForm):
    english = StringField('English', validators=[DataRequired()])
    armenian = StringField('Armenian', validators=[DataRequired()])
    private = BooleanField('Private')
    submit = SubmitField('Add')
