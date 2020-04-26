from flask import render_template, url_for, flash, redirect, request
from sqlalchemy import func, and_
from GroceryTracking import app, db, bcrypt
from flask_login import login_user, current_user, logout_user, login_required
from GroceryTracking.models import List, User, Item, Content
from GroceryTracking.forms import LogInForm, RegistrationForm, EditAccountForm, AddListForm, DeleteListForm, RenameListForm,\
    ChangePasswordForm, ValidationError, AddItemManuallyForm
from GroceryTracking.helperFunctions import nextHighestUserId, getInformationOnUpc, addItemToDatabaseAndList, \
    nextHighestListId
from GroceryTracking.testFunctions import recreateDatabaseBlank, recreateDatabaseTestFill

@app.route("/")
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


@app.route("/userLists/displayAllItems", methods=['POST', 'GET'])
@login_required
def displayAllItems():
    currentUser = current_user
    userLists = []
    itemContentList = []
    itemNameAndQuantityList = []
    userListsWithCommas = db.session.query(List.id).filter(currentUser.id == List.user_id).all()
    for listID in userListsWithCommas:
        listIDWithoutCommas = listID[0]
        userLists.append(listIDWithoutCommas)
    for listID in userLists:
        ContentList = db.session.query(Content).filter(Content.list_id == listID).all()
        for contentEntry in ContentList:
            itemContentList.append(contentEntry)
    for item in itemContentList:
        itemUPC = item.item_upc
        itemQuantity = item.quantity
        testQuery = db.session.query(Item.name).filter(Item.upc == itemUPC).first()
        if testQuery != None:
            itemName = db.session.query(Item.name).filter(Item.upc == itemUPC).all()[0][0]
            itemNameAndQuantityList.append([itemName, itemQuantity])

    return render_template('DisplayAllitems.html', itemNameAndQuantityList=itemNameAndQuantityList)


@app.route("/addItemManually", methods=['POST', 'GET'])
@login_required
def AddItemManually():
    form = AddItemManuallyForm()
    itemName = form.itemName.data
    itemUPC = form.itemUPC.data
    itemQuantity = form.itemQuantity.data
    ListName = form.ListName.data
    if form.validate_on_submit():
        testQuery = db.session.query(Item).filter(Item.upc == itemUPC).first()
        print(testQuery)
        if testQuery == None:
            newItem = Item(upc=itemUPC, name=itemName)
            db.session.add(newItem)
        ListID = db.session.query(List.id).filter(List.name == ListName).all()[0][0]
        print(current_user)
        testQuery = db.session.query(Content).filter(Content.item_upc == itemUPC,
                                                     Content.list_id == ListID).first()
        if testQuery == None:
            newContentEntry = Content(item_upc=itemUPC, list_id=ListID,
                                  quantity=itemQuantity)
            db.session.add(newContentEntry)
        else:
            testQuery.quantity += 1
        db.session.commit()
        flash('Your item added', 'success')

    return render_template('AddItemManually.html', title='New Item', form=form, legend='New Item')



@app.route("/listContents/<int:listId>")
def listContents(listId):
    currentList = listId
    contents = db.session.query(Item.name, Content.quantity, Content.list_id).join(Item).filter(
        and_(Item.upc == Content.item_upc, Content.list_id == currentList))
    for x in contents:
        print(x)
    return render_template('ListContents.html', contents=contents)


@app.route("/listContents/delete/<int:listId>/<string:itemName>", methods=['POST', 'GET'])
@login_required
def deleteItem(itemName, listId):
    print("itemName: ", itemName)
    currentList = listId
    contents = db.session.query(Item.name, Content.quantity, Content.list_id).join(Item).filter(
        and_(Item.upc == Content.item_upc, Content.list_id == currentList))

    itemUPC = db.session.query(Item.upc).filter(Item.name == itemName).all()[0][0]
    listContents = db.session.query(Content).filter(Content.item_upc == itemUPC,
                                                    Content.list_id == listId).all()[0]
    print("listContents before: ", listContents)
    itemListQuantity = listContents.quantity
    print(itemListQuantity)
    itemListQuantity = itemListQuantity - 1
    print(itemListQuantity)
    listContents.quantity = itemListQuantity
    print("listContents after: ", listContents)
    db.session.commit()
    flash('Your item quantity been updated!', 'success')
    return redirect(url_for('listContents', listId=listId))


@app.route("/listContents/add/<int:listId>/<string:itemName>", methods=['POST', 'GET'])
@login_required
def AddOneItem(itemName, listId):
    print("itemName: ", itemName)
    currentList = listId
    contents = db.session.query(Item.name, Content.quantity, Content.list_id).join(Item).filter(
        and_(Item.upc == Content.item_upc, Content.list_id == currentList))

    itemUPC = db.session.query(Item.upc).filter(Item.name == itemName).all()[0][0]
    listContents = db.session.query(Content).filter(Content.item_upc == itemUPC,
                                                    Content.list_id == listId).all()[0]
    print("listContents before: ", listContents)
    itemListQuantity = listContents.quantity
    print(itemListQuantity)
    itemListQuantity = itemListQuantity + 1
    print(itemListQuantity)
    listContents.quantity = itemListQuantity
    print("listContents after: ", listContents)
    db.session.commit()
    flash('Your item quantity been updated!', 'success')
    return redirect(url_for('listContents', listId=listId))


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
        print(form.listOfLists.data)
        #-1 is the value assigned to the value in the choices list of "Pick a list"
        if form.listOfLists.data == '-1':
            flash('Please select a list.', 'fail')
        elif form.listOfLists.data != 'None':
            listToDeleteId = form.listOfLists.data
            selectedListFromDatabase = List.query.filter_by(id=listToDeleteId).first()
            db.session.delete(selectedListFromDatabase)
            db.session.commit()
            flash('Your List has been deleted!', 'success')
            return redirect(url_for('userLists'))
        else:
            flash('There are no lists to delete.', 'success')
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
    # get form
    form = EditAccountForm()
    if request.method == 'POST':
        # check if they changed anything
        changeFlag = False

        # Get username and email from form
        newUsername = form.username.data
        newEmail = form.email.data

        # Check if we should change email
        if newEmail != current_user.email:
            try:
                # Check email
                form.validate_email(newEmail)
                # set flag to commit database
                changeFlag=True
                # Change email
                current_user.email=newEmail
                # Tell user
                flash('Email updated.', 'success')
            # catch invalid email
            except ValidationError:
                # undo changes
                db.session.rollback()
                # Tell user
                flash('That email is already in use. Please try another.', 'fail')

        # Check if we should change user
        if newUsername != current_user.username:
            try:
                # Check username
                form.validate_username(newUsername)
                # set flag to commit database
                changeFlag=True
                # Change email
                current_user.username=newUsername
                # Tell user
                flash('Username updated.', 'success')
            except ValidationError: 
                # undo changes
                db.session.rollback()
                # Tell user
                flash('That username is already in use. Please try another.', 'fail')
        if changeFlag:
            # save change
            db.session.commit()  
            # Send user back to menu
            return redirect(url_for('settings'))
            
    # Get username and email to show in rendered form
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email

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
    