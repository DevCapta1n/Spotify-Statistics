"""SQLAlchemy models for statify."""

from flask_sqlalchemy import SQLAlchemy
import json
import sqlalchemy
from sqlalchemy.types import TypeDecorator, VARCHAR

db = SQLAlchemy()

DEFAULT_IMAGE_URL = "https://www.freeiconspng.com/uploads/icon-user-blue-symbol-people-person-generic--public-domain--21.png"

class TextPickleType(TypeDecorator):
    """ a custom column type for storing a json string of multiple artists for
    a single song"""

    impl = VARCHAR

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value

class User(db.Model):
    """user of the website"""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    display_name = db.Column(db.Text, nullable=False)
    profile_pic_url = db.Column(db.Text, nullable=False)

    top_artists = db.relationship("TopArtist", backref="user", cascade="all, delete-orphan")
    top_tracks = db.relationship("TopTrack", backref="user", cascade="all, delete-orphan")

class TopTrack(db.Model):
    """the top tracks for users with a ranking column"""

    __tablename__ = "top_tracks"

    id = db.Column(db.Integer, primary_key=True)
    rank = db.Column(db.Integer, nullable=False)
    name = db.Column(db.Text, nullable=False)
    album_cover = db.Column(db.Text, nullable=False)
    artists = db.Column(db.PickleType, nullable=False)
    time_range = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

class TopArtist(db.Model):
    """a table which holds information about an artist along with their ranking for user"""

    __tablename__ = "top_artists"

    id = db.Column(db.Integer, primary_key=True)
    rank = db.Column(db.Integer, nullable=False)
    artist_name = db.Column(db.Text, nullable=False)
    image = db.Column(db.Text, nullable=False)
    time_range = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

def connect_db(app):
    """Connect this database to provided Flask app."""

    db.app = app
    db.init_app(app)