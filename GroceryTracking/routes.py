from flask import render_template, url_for, flash, redirect, request
from sqlalchemy import func, and_
from GroceryTracking import app, db, bcrypt
from flask_login import login_user, current_user, logout_user, login_required
from GroceryTracking.models import List, User, Item, Content
from GroceryTracking.forms import LogInForm, RegistrationForm
from GroceryTracking.helperFunctions import nextHighestUserId
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

