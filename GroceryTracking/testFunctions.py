from GroceryTracking import db, bcrypt
from sqlalchemy import func
from GroceryTracking.models import User, List, Item, Content
from GroceryTracking.helperFunctions import nextHighestListId, nextHighestUserId

def recreateDatabaseBlank():
    db.drop_all()
    db.create_all()

def recreateDatabaseTestFill():
    db.drop_all()
    db.create_all()

    #create test user
    userId = nextHighestUserId()
    hashed_password = bcrypt.generate_password_hash('password').decode('utf-8')
    testUser = User(id=userId, first_name="John", username="Johnny", email="john@gmail.com", password=hashed_password)
    db.session.add(testUser)
    db.session.commit()

    #create two test lists
    listId1 = nextHighestListId()
    testList1 = List(id=listId1, user_id=userId, name="TestList1", size=0)
    db.session.add(testList1)
    db.session.commit()

    listId2 = nextHighestListId()
    testList2 = List(id=listId2, user_id=userId, name="TestList2", size=0)
    db.session.add(testList2)
    db.session.commit()

    #create test items
    testItem1Upc = "757528029753"
    testItem1Name = "Takis Fiesta Size Fuego - 20oz"
    testItem1 = Item(upc=testItem1Upc, name=testItem1Name)
    db.session.add(testItem1)
    db.session.commit()

    testItem2Upc = "022000005120"
    testItem2Name = "PEPPERMINT COBALT SUGARFREE GUM"
    testItem2 = Item(upc=testItem2Upc, name=testItem2Name)
    db.session.add(testItem2)
    db.session.commit()

    #fill the lists with the test items
    addedItem1 = Content(item_upc=testItem1Upc, list_id=listId1, quantity=10)
    db.session.add(addedItem1)
    addedItem2 = Content(item_upc=testItem1Upc, list_id=listId2, quantity=7)
    db.session.add(addedItem2)
    addedItem3 = Content(item_upc=testItem2Upc, list_id=listId2, quantity=3)
    db.session.add(addedItem3)
    db.session.commit()

