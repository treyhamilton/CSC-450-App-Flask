from GroceryTracking import db
from sqlalchemy import func
from GroceryTracking.models import User

def nextHighestUserId():
    maxUserId = db.session.query(func.max(User.id))
    maxId = maxUserId[0]
    maxId = maxId[0]
    if maxId == None:
        nextMaxId = 1
    else:
        nextMaxId = maxId+10
    return nextMaxId

def recreateDatabase():
    db.drop_all()
    db.create_all()
