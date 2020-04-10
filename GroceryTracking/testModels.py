from GroceryTracking.models import User
from GroceryTracking import db
from sqlalchemy import desc

def assertEqual(test_name, input_value, desired_value):
    if input_value == desired_value:
        print(test_name + ": Pass")
        return True
    if type(input_value) != type(desired_value):
        print("Fail: Type error.")
        return False
    else:
        print("Fail: input_value does not equal desired_value.")
        return False

def testUser():
    db.drop_all()
    db.create_all()

    user1 = User(id=1, first_name="john", username="john234", email="john234@gmail.com", password="iguessjohn")
    user2 = User(id=2, first_name="johnny", username="john234234", email="john234234@gmail.com", password="iguessjohn2")
    testName = "testUser"

    db.session.add(user1)
    db.session.add(user2)
    db.session.commit()
    firstUser = User.query.first()
    lastUser = User.query.filter().order_by(desc(User.id)).first()
    print(lastUser)

    assertEqual(testName, firstUser, user1)
    assertEqual(testName, lastUser, user2)
