from GroceryTracking import db
from sqlalchemy import func
from GroceryTracking.models import User, List, Item, Content
import requests, json


def nextHighestUserId():
    maxUserId = db.session.query(func.max(User.id))
    maxId = maxUserId[0]
    maxId = maxId[0]
    if maxId == None:
        nextMaxId = 1
    else:
        nextMaxId = maxId + 1
    return nextMaxId


def nextHighestListId():
    maxListId = db.session.query(func.max(List.id))
    maxId = maxListId[0]
    maxId = maxId[0]
    if maxId == None:
        nextMaxId = 1
    else:
        nextMaxId = maxId + 1
    return nextMaxId


def getInformationOnUpc(upc):
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }
    resp = requests.get('https://api.upcitemdb.com/prod/trial/lookup?upc=' + str(upc), headers=headers)
    data = json.loads(resp.text)
    for item in data['items']:
        print("{}\t{}\t{}\t{}-{}".format(item['ean'], item['title'], item['brand'], item['lowest_recorded_price'],
                                         item['highest_recorded_price']))
        return (item)


def addItemToDatabaseAndList(item):
    itemUpc = str(item['ean'])
    print('itemUpc is' + itemUpc)
    doesItemExistInDatabase = Item.query.filter_by(upc=itemUpc).first()
    print("Does item exist in database?" + str(doesItemExistInDatabase))
    if doesItemExistInDatabase:
        print("item exists in database already.")
    else:
        print("item does not exist in database already.")
        newItem = Item(upc=item['ean'], name=item['title'])
        db.session.add(newItem)
        db.session.commit()

