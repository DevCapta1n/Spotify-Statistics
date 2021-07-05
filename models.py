"""SQLAlchemy models for statify."""

from flask_sqlalchemy import SQLAlchemy
import json
import sqlalchemy
from sqlalchemy.types import TypeDecorator, VARCHAR

db = SQLAlchemy()

DEFAULT_IMAGE_URL = "https://www.freeiconspng.com/uploads/icon-user-blue-symbol-people-person-generic--public-domain--21.png"

class User(db.Model):
    """user of the website"""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    display_name = db.Column(db.Text, nullable=False)
    profile_pic_url = db.Column(db.Text, nullable=False)
    token = db.Column(db.Text, nullable=False)

class FavoriteGenre(db.Model):
    """a table listing information about a genre including its rank and related user"""

    __tablename__ = "favorite_genres"

    id = db.Column(db.Integer, primary_key=True)
    rank = db.Column(db.Integer, nullable=False)
    genre_name = db.Column(db.Text, nullable=False)
    icon = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

def connect_db(app):
    """Connect this database to provided Flask app."""

    db.app = app
    db.init_app(app)