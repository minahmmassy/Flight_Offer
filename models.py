
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt


db = SQLAlchemy()

bcrypt = Bcrypt()

def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)

# Models

class User(db.Model):
    __tablename__='users'

    id = db.Column(db.Integer,
        primary_key=True,
        autoincrement=True)

    first_name = db.Column(db.String(15),
        nullable=False)

    last_name = db.Column(db.String(20),
        nullable=True)

    email = db.Column(db.String(50),
        nullable=False,
        unique=True)

    username = db.Column(db.String(20),
        nullable=False,
        unique=True)

    password = db.Column(db.Text,
        nullable=False)

    wishlist = db.relationship('Wishlist', backref='user')

    

    @classmethod
    def registration(cls,first_name,last_name,email,username,pwd,confirm_password):
        if pwd == confirm_password:
            hashed = bcrypt.generate_password_hash(pwd)
            hashed_utf8 = hashed.decode("utf8")
            user = cls(first_name=first_name,last_name=last_name,email=email,username=username,password=hashed_utf8)
            db.session.add(user)
            return user
        


    # Authentication/Login
    @classmethod
    def authenticate(cls,username,pwd):
        u = User.query.filter_by(username=username).first()
        # Check if username and password are correct log user in otherwise return False
        if u and bcrypt.check_password_hash(u.password,pwd):
            return u
        else:
            return False


class Wishlist(db.Model):

    __tablename__='wishlist'

    id = db.Column(db.Integer,primary_key=True)
    origin = db.Column(db.String(15))
    destination = db.Column(db.String(20))
    departure_date = db.Column(db.Text)
    ticket_price = db.Column(db.Text)
    notes = db.Column(db.String(120))

    user_id = db.Column(db.ForeignKey('users.id'),nullable=False)
    

