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
    display_name = db.Column(db.String(30), nullable=False, unique=True)
    profile_pic_url = db.Column(db.Text, nullable=False)
    token = db.Column(db.Text, nullable=False)
    country = db.Column(db.Text, nullable=False)
    spotify_link = db.Column(db.Text, nullable=False)
    followers = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'display_name': self.display_name,
            'profile_pic_url': self.profile_pic_url,
            'token': self.token,
            'country': self.country,
            'spotify_link': self.spotify_link,
            'followers': self.followers
        }

def connect_db(app):
    """Connect this database to provided Flask app."""

    db.app = app
    db.init_app(app)