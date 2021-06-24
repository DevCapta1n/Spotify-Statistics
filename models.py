"""SQLAlchemy models for statify."""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    """user of the website"""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    display_name = db.Column(db.Text, nullable=False)
    profile_pic_url = db.Column(db.Text, nullable=False)
    country = db.Column(db.Text, nullable=False)

    top_artists = db.relationship("Top_Artist", backref="user", cascade="all, delete-orphan")
    top_tracks = db.relationship("Top_Track", backref="user", cascade="all, delete-orphan")
    fav_genres = db.relationship("Favorite_Genre", backref="user", cascade="all, delete-orphan")
    recommendations = db.relationship("Recommendation", backref="user", cascade="all, delete-orphan")

class Recommendation(db.Model):
    """recommended albums for the user"""

    __tablename__ = "recommendations"

    id = db.Column(db.Integer, primary_key=True)
    album_name = db.Column(db.Text, nullable=False)
    genre_name = db.Column(db.Text, nullable=False)
    artists = db.relationship("Artist", backref="user", cascade="all, delete-orphan")
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

class Artist(db.Model):
    """a table of artist names"""

    __tablename__ = "artists"

    id = db.Column(db.Integer, primary_key=True)
    artist_name = db.Column(db.Text, nullable=False)

class TopArtist(db.Model):
    """a table which holds information about an artist along with their ranking for user"""

    __tablename__ = "top_artists"

    id = db.Column(db.Integer, primary_key=True)
    rank = db.Column(db.Integer, nullable=False)
    artist_name = db.Column(db.Text, nullable=False)
    image = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

class FavoriteGenre(db.Model):
    """a table listing information about a genre including its rank and related user"""

    __tablename__ = "favorite_genres"

    id = db.Column(db.Integer, primary_key=True)
    rank = db.Column(db.Integer, nullable=False)
    genre_name = db.Column(db.Text, nullable=False)
    icon = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

class TopTrack(db.Model):
    """the top tracks for users with a ranking column"""

    __tablename__ = "top_tracks"

    id = db.Column(db.Integer, primary_key=True)
    rank = db.Column(db.Integer, nullable=False)
    genre_name = db.Column(db.Text, nullable=False)
    album_cover = db.Column(db.Text, nullable=False)
    artists = db.relationship("Artist", backref="user", cascade="all, delete-orphan")
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

def connect_db(app):
    """Connect this database to provided Flask app."""

    db.app = app
    db.init_app(app)