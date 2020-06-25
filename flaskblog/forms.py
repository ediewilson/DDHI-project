from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flaskblog.models import User
from flask_login import current_user
from flask_wtf.file import FileField, FileAllowed


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])

    password = PasswordField('Password', validators=[DataRequired()])
    confirmPassword = PasswordField('Confirm password', validators=[DataRequired(), EqualTo('password')])

    submit = SubmitField('Sign Up')

    def validateUsername(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken, choose a different one.')

    def validateUsername(self, email):
        email = User.query.filter_by(email=email.data).first()
        if email:
            raise ValidationError('That email is already in user, choose a different one.')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    
    remember = BooleanField('Remember me')

    submit = SubmitField('Log in')



class UpdateAccountForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    picture = FileField('Update profile picture', validators=[FileAllowed(['png','jpg'])])

    submit = SubmitField('Update')

    def validateUsername(self, username):
        if username.data is not current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken, choose a different one.')

    def validateUsername(self, email):
        if email.data is not current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is already in user, choose a different one.')



class PlaceVizForm(FlaskForm):
    dataFile = FileField('Upload data visualization file', validators=[FileAllowed(['csv'])])
    submit = SubmitField('Upload')


class NewPlaceForm(FlaskForm):
    address = StringField('Address')
    city = StringField('City')
    latitude = StringField('Latitude', validators=[DataRequired()])
    longitude = StringField('Longitude', validators=[DataRequired()])
    source =  StringField('Source', validators=[DataRequired()])

    submit = SubmitField('Add place')


class FileNameForm(FlaskForm):
    newFileName = StringField('Last name of interviewee', validators=[DataRequired()])
    
    submit = SubmitField('Done')