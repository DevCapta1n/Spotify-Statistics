"""SQLAlchemy models for statify."""

from flask_sqlalchemy import SQLAlchemy
import json
import sqlalchemy
from sqlalchemy.types import TypeDecorator, VARCHAR
# from flask import current_app as app
# from flask_bcrypt import Bcrypt
# bcrypt = Bcrypt(app)
from app import bcrypt

db = SQLAlchemy()

DEFAULT_IMAGE_URL = "https://www.freeiconspng.com/uploads/icon-user-blue-symbol-people-person-generic--public-domain--21.png"

class User(db.Model):
    """user of the website"""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    display_name = db.Column(db.String(30), nullable=False)
    password = db.Column(db.Text, nullable=False)
    profile_pic_url = db.Column(db.Text, nullable=False)
    token = db.Column(db.Text, nullable=False)
    country = db.Column(db.Text, nullable=False)
    spotify_link = db.Column(db.Text, nullable=False, unique=True)
    followers = db.Column(db.Integer, nullable=False)
    new = db.Column(db.Boolean, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'display_name': self.display_name,
            'profile_pic_url': self.profile_pic_url,
            'country': self.country,
            'spotify_link': self.spotify_link,
            'followers': self.followers
        }

    @classmethod
    def register(cls, username, pwd):
        """Register user w/hashed password & return user."""

        hashed = bcrypt.generate_password_hash(pwd)
        # turn bytestring into normal (unicode utf8) string
        hashed_utf8 = hashed.decode("utf8")

        # return instance of user w/username and hashed pwd
        return {username:username, password:hashed_utf8}
    
    @classmethod
    def authenticate(cls, username, pwd):
        """Validate that user exists & password is correct.

        Return user if valid; else return False.
        """

        u = User.query.filter_by(display_name=username).first()
        print(u)
        #print(u.password)
        #print(bcrypt.check_password_hash(u.password, pwd))
        if u and bcrypt.check_password_hash(u.password, pwd):
            # return user instance
            return u
        else:
            return False

def connect_db(app):
    """Connect this database to provided Flask app."""

    db.app = app
    db.init_app(app)