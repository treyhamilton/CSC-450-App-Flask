from flask import render_template, url_for, flash, redirect, request
from sqlalchemy import func, and_
from GroceryTracking import app, db, bcrypt
from flask_login import login_user, current_user, logout_user, login_required
from GroceryTracking.models import List, User, Item, Content
from GroceryTracking.forms import LogInForm, RegistrationForm, EditAccountForm, ChangePasswordForm, ValidationError
from GroceryTracking.helperFunctions import nextHighestUserId, getInformationOnUpc, addItemToDatabaseAndList
from GroceryTracking.testFunctions import recreateDatabaseBlank, recreateDatabaseTestFill


@app.route("/MainMenu")
@login_required
def mainMenuRoute():
    return render_template('MainMenu.html')

@app.route("/registerRoute", methods=['GET', 'POST'])
def registerRoute():
    if current_user.is_authenticated:
        return redirect(url_for('mainMenuRoute'))
    form = RegistrationForm()
    if form.validate_on_submit():
        userId = nextHighestUserId()
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        newUser = User(id = userId, username=form.username.data, email=form.email.data, password=hashed_password)
        try:
            db.session.add(newUser)
            db.session.commit()
            flash('Your account has been created! You are now able to log in', 'success')
            return redirect(url_for('mainMenuRoute'))
        except:
            db.session.rollback()
            flash('Your account has not been created.', 'fail')
        return redirect(url_for('login'))
    return render_template('Register.html', title='Register', form=form)

@app.route("/")
@app.route("/login", methods=['GET', 'POST'])
def login():
    ##Tests by adding fake users, lists, items. Comment out and save for testing purposes after turning server on.
    #recreateDatabaseTestFill()
    if current_user.is_authenticated:
        return redirect(url_for('mainMenuRoute'))
    form = LogInForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('mainMenuRoute'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('Login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route("/userLists")
def userLists():
    lists = List.query.filter_by(user_id = current_user.id)
    return render_template('YourLists.html', lists=lists)

@app.route("/listContents/<int:listId>")
def listContents(listId):
    currentList = listId
    contents = db.session.query(Item.name, Content.quantity).join(Item).filter(and_(Item.upc==Content.item_upc, Content.list_id==currentList))
    for x in contents:
        print(x)
    return render_template('ListContents.html', contents=contents)

@app.route("/settings")
def settings():
    return render_template('Settings.html')

@app.route("/settings/editAccount", methods=['GET', 'POST'])
@login_required
def editAccount():
    user = User.query.filter_by(id=current_user.id).first()

    form = EditAccountForm()
    if request.method == 'POST':
        user.username = form.username.data
        user.email = form.email.data
        try:
            form.validate_email(user.email)
            try:
                form.validate_email(user.email)
                db.session.commit()
                flash('Your account has been updated.', 'success')
                return redirect(url_for('editAccount'))
            except:
                db.session.rollback()
                flash('Your changes failed to save.', 'fail')
        except:
            flash('That email is already in use. Please try another.', 'fail')
        return redirect(url_for('editAccount'))
    
    elif request.method == 'GET':
        form.username.data = user.username
        form.email.data = user.email
        
    return render_template('EditAccount.html', title='Edit Account', form=form)

@app.route("/getItem", methods=['GET', 'POST'])
@login_required
def getItem():
    try:
        print('getting information from API')
        itemInformation = getInformationOnUpc('640522710850')
        print('Adding item to database.')
        addItemToDatabaseAndList(itemInformation)
        flash('Successfully added Item to list.', 'success')
        return render_template('MainMenu.html')
    except:
        flash('Failed to add item to list. Already exists in Database.', 'fail')
        return render_template('MainMenu.html')

@app.route("/changePassword", methods=['GET', 'POST'])
@login_required
def changePassword():
    form = ChangePasswordForm()
    # Check form
    if form.validate_on_submit():
        # Check if the current password is correct
        if bcrypt.check_password_hash(current_user.password, form.oldPassword.data):
           # Hash the new password
            newPassword = bcrypt.generate_password_hash(form.newPassword.data).decode('utf-8')
            # Update the new password
            current_user.password = newPassword
            # Save changes
            db.session.commit()
            flash('Successfully changed password.', 'success')
        else:
            flash('Current password is not correct.', 'warning')
    # check if user attempted to change password
    elif "newPassword" in request.form:
        flash('Passwords do not match.', 'warning')
    return render_template('changePassword.html', title='Change Password', form=form)