from flask_wtf import FlaskForm
from bubble.models import User
from wtforms import StringField, PasswordField, SubmitField, BooleanField, ValidationError, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from flask_login import current_user

class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=30)])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')


    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username Already Taken')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email Already Taken')


class LoginForm(FlaskForm):
    email = StringField(label="Email", validators=[DataRequired(), Email()])
    password = PasswordField(label="Password", validators=[DataRequired(), Length(min=6)])
    remember = BooleanField('Remember Me')
    submit = SubmitField(label="Login")

class NewPost(FlaskForm):
    title = StringField(label="Title", validators=[DataRequired()])
    content = TextAreaField(label="Content", validators=[DataRequired()])
    submit = SubmitField(label="Create a new memory")


class ResetPasswordQuery(FlaskForm):
    email = StringField(label="Email", validators=[DataRequired(), Email()])
    submit = SubmitField('Request')
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        submit = SubmitField('Request Password')
        if user is None:
            raise ValidationError(f'Account with {user.email} does not exist.')

class PasswordUpdate(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=30)])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')

class UpdateProfile(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Update Profile')


    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if username.data == current_user.username:
            pass
        else:        
            if user:
                raise ValidationError('Username Already Taken')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if email.data == current_user.email:
            pass
        else:               
            if user:
                raise ValidationError('Email Already Taken')