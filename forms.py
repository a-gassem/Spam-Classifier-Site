from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired

class LoginForm(FlaskForm):
    email = StringField("Email:", validators=[InputRequired()])
    password = StringField("Password:", validators=[InputRequired()])
    submit = SubmitField("Login")
        
class RegisterForm(FlaskForm):
    email = StringField("Email:", validators=[InputRequired()])
    submit = SubmitField("Continue")

class ConfirmForm(FlaskForm):
    code = StringField("Check Code:", validators=[InputRequired()])
    submit = SubmitField("Confirm")

class PasswordForm(FlaskForm):
    newPassword = StringField("New Password:", validators=[InputRequired()])
    confirmPassword = StringField("Confirm Password:", validators=[InputRequired()])
    submit = SubmitField("Finish")

class ScanForm(FlaskForm):
    messageID = StringField("Message ID:", validators=[InputRequired()])
    submit = SubmitField("Scan email")

class AddressForm(FlaskForm):
    address = StringField("Add address:", validators=[InputRequired()])
    whitelistSubmit = SubmitField("Add to Whitelist")
    blacklistSubmit = SubmitField("Add to Blacklist")

class SearchForm(FlaskForm):
    query = StringField("Search:", validators=[InputRequired()])
    searchSubmit = SubmitField("Search...")
