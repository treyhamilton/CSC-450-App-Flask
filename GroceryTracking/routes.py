from flask import render_template, url_for, flash, redirect, request
from sqlalchemy import func, and_
from GroceryTracking import app, db, bcrypt
from flask_login import login_user, current_user, logout_user, login_required
from GroceryTracking.models import List, User, Item, Content
from GroceryTracking.forms import LogInForm, RegistrationForm, EditAccountForm, AddListForm, DeleteListForm, RenameListForm
from GroceryTracking.helperFunctions import nextHighestUserId, getInformationOnUpc, addItemToDatabaseAndList, \
    nextHighestListId
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
        newUser = User(id=userId, username=form.username.data, email=form.email.data, password=hashed_password)
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
    # recreateDatabaseTestFill()
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
    lists = List.query.filter_by(user_id=current_user.id)
    return render_template('YourLists.html', lists=lists)


@app.route("/listContents/<int:listId>")
def listContents(listId):
    currentList = listId
    contents = db.session.query(Item.name, Content.quantity).join(Item).filter(
        and_(Item.upc == Content.item_upc, Content.list_id == currentList))
    for x in contents:
        print(x)
    return render_template('ListContents.html', contents=contents)


@app.route("/settings")
def settings():
    return render_template('Settings.html')


@app.route("/listManagement")
@login_required
def listManagement():
    return render_template('listManagement.html')


@app.route("/addList", methods=['GET', 'POST'])
@login_required
def addList():
    form = AddListForm()

    if form.validate_on_submit():
        addID = nextHighestListId()

        nameAdd = form.nameAdd.data
        newList = List(id=addID, user_id=current_user.id, name=nameAdd, size=0)

        db.session.add(newList)
        db.session.commit()
        flash('Your List has been created!', 'success')
        return redirect(url_for('userLists'))
    return render_template('addList.html', title='New List', form=form, legend='New List')


@app.route("/deleteList", methods=['GET', 'POST'])
@login_required
def deleteList():
    form = DeleteListForm()
    form.addUsersListsToForm()

    if request.method == 'POST':
        listToDeleteId = form.listOfLists.data
        selectedListFromDatabase = List.query.filter_by(id=listToDeleteId).first()
        db.session.delete(selectedListFromDatabase)
        db.session.commit()
        flash('Your List has been deleted!', 'success')
        return redirect(url_for('userLists'))
    return render_template('deleteList.html', title='Delete List', form=form, legend='Delete List')

@app.route("/renameList", methods=['GET', 'POST'])
@login_required
def renameList():
    form = RenameListForm()
    form.addUsersListsToForm()
    print(form.newList.data)

    if request.method == 'POST':
        listToRenameID = form.oldList.data
        selectedListFromDatabase = List.query.filter_by(id=listToRenameID).first()
        print(form.newList.data)
        try:
            selectedListFromDatabase.name = form.newList.data
            db.session.commit()
            flash('Your List has been updated.', 'success')
            return redirect(url_for('userLists'))
        except:
            db.session.rollback()
            flash('Your changes failed to save.', 'fail')
            return redirect(url_for('userLists'))

    return render_template('renameList.html', title='Rename List', form=form, legend='Rename List')


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