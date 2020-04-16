from GroceryTracking import db
from sqlalchemy import func
from GroceryTracking.models import User, List

def nextHighestUserId():
    maxUserId = db.session.query(func.max(User.id))
    maxId = maxUserId[0]
    maxId = maxId[0]
    if maxId == None:
        nextMaxId = 1
    else:
        nextMaxId = maxId+1
    return nextMaxId

def nextHighestListId():
    maxListId = db.session.query(func.max(List.id))
    maxId = maxListId[0]
    maxId = maxId[0]
    if maxId == None:
        nextMaxId = 1
    else:
        nextMaxId = maxId+1
    return nextMaxId

