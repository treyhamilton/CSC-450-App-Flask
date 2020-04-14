from flask import render_template, url_for, flash, redirect, request
from sqlalchemy import func
from GroceryTracking import app, db, bcrypt
from flask_login import login_user, current_user, logout_user, login_required
from GroceryTracking.models import List, User
from GroceryTracking.forms import LogInForm, RegistrationForm
from GroceryTracking.helperFunctions import nextHighestUserId, recreateDatabase


@app.route("/MainMenu")
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
    return render_template('register.html', title='Register', form=form)

@app.route("/")
@app.route("/login", methods=['GET', 'POST'])
def login():
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
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))



