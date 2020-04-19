from GroceryTracking import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    first_name = db.Column(db.String(15), nullable=True)
    username = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(40), nullable=False)
    password = db.Column(db.String(60), nullable=False)

    lists = db.relationship("List", backref="user")

    def __repr__(self):
        return f'User(id:{self.id}, first_name:{self.first_name}, username:{self.username}, email:{self.email}, password:{self.password})'


class List(db.Model):
    __tablename__ = "list"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True, nullable=False)
    name = db.Column(db.String, nullable=False)
    size = db.Column(db.Integer, nullable=True)

    list_content = db.relationship("Content", backref="list", cascade="all, delete")

    def __repr__(self):
        return f'List(id:{self.id}, user_id:{self.user_id}, name:{self.name}, size:{self.size})'


class Content(db.Model):
    __tablename__ = "content"
    item_upc = db.Column(db.Integer, db.ForeignKey("item.upc"), primary_key=True, nullable=False)
    list_id = db.Column(db.Integer, db.ForeignKey("list.id"), primary_key=True, nullable=False)
    quantity = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return f'Content(item_upc:{self.item_upc}, list_id:{self.list_id}, quantity:{self.quantity})'


class Item(db.Model):
    __tablename__ = "item"
    upc = db.Column(db.String, primary_key=True, nullable=False)
    name = db.Column(db.String, nullable=False)

    item_info = db.relationship("Content", backref="item")

    def __repr__(self):
        return f'Item(upc:{self.upc}, name:{self.name})'