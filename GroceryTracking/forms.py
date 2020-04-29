from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, PasswordField, SubmitField, BooleanField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, optional
from GroceryTracking.models import User, List
from flask_login import login_user, current_user, logout_user, login_required


class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=5, max=30)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Sign Up")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')

class LogInForm(FlaskForm):
    email = StringField("Email", validators = [DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember My Login")
    submit = SubmitField("Login")


class RenameListForm(FlaskForm):
    oldList = SelectField("List to be Renamed", choices=[])
    newList = StringField("New Name")
    changeButton = SubmitField("Submit")
    def addUsersListsToForm(self):
        self.oldList.choices = [(usersList.id, usersList.name)
                                   for usersList in
                                   List.query.filter_by(user_id=current_user.id).all()]



class AddListForm(FlaskForm):
    nameAdd = TextAreaField("Name")
    addButton = SubmitField("Add List")

class DeleteListForm(FlaskForm):
    listOfLists = SelectField("Name", choices=[])
    deleteButton = SubmitField("Delete List")
    def addUsersListsToForm(self):
        self.listOfLists.choices= [(usersList.id, usersList.name)
                                   for usersList in
                                   List.query.filter_by(user_id=current_user.id).all()]

    def addUsersListsToForm(self):
        self.listOfLists.choices= [(usersList.id, usersList.name) for usersList in List.query.filter_by(user_id=current_user.id).all()]
        self.listOfLists.choices.insert(0, (-1, 'Pick a list'))

class EditAccountForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=5, max=30)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Submit")

    def validate_username(self, username):
        user = User.query.filter_by(username=username).first()
        if user or username == "":
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email).first()
        if user or email == "":
            raise ValidationError('That email is taken. Please choose a different one.')

class ChangePasswordForm(FlaskForm):
    oldPassword = PasswordField("Current Password", validators=[DataRequired()])
    newPassword = PasswordField("New Password", validators=[DataRequired()])
    confirmNewPassword = PasswordField("Re-Type Password", validators=[DataRequired(), EqualTo("newPassword")])
    submit = SubmitField("Submit")

class AddItemManuallyForm(FlaskForm):
    itemName = StringField("Item Name", validators=[DataRequired()])
    itemUPC = IntegerField("Item UPC", validators=[DataRequired()])
    itemQuantity = IntegerField("Number of items", validators=[optional()])
    ListName = StringField("Name of List:", validators=[DataRequired()])
    submit = SubmitField("Submit")

class lookupUPC(FlaskForm):
    upc = StringField("UPC Number", validators = [DataRequired()])
    submit = SubmitField("Look up")