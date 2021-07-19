"""functions for updating the statify database with data from the spotify api"""

from models import db, connect_db, User
# from app import app
# from flask_bcrypt import Bcrypt
# bcrypt = Bcrypt(app)
from app import bcrypt
def update_user(user_json, token):
    """update, create, or do nothing, then return the passed in user"""

    target_user = User.query.filter_by(spotify_link=user_json['external_urls']['spotify']).first()
    
    if not target_user:
        try:
            #some responses may include a country key and value pair
            country = user_json['country']
        except KeyError:
            country = 'United States'

        hashed_password = bcrypt.generate_password_hash(user_json['display_name'])
        hash_pass_utf8 = hashed_password.decode("utf8")
        #procede if the target_user does not exist in the database
        new_user = User(
            display_name = user_json['display_name'],
            password = hash_pass_utf8,
            profile_pic_url = user_json['images'][0]['url'],
            token = token,
            country = country,
            spotify_link = user_json['external_urls']['spotify'],
            followers = user_json['followers']['total'],
            new = True
        )
        db.session.add(new_user)
        db.session.commit()

        return new_user

    if not User.query.filter_by(display_name=user_json['display_name'],profile_pic_url=user_json['images'][0]['url']).first():

        #if the user exists but their profile picture is out of date, update it
        target_user.profile_pic_url = user_json['images'][0]['url']
        db.session.add(target_user)
        db.session.commit()

    if not User.query.filter_by(token=token).first():

        #an existing user's token should be out of date every session
        #so it needs to be updated
        target_user.token = token
        db.session.add(target_user)
        db.session.commit()

    if not User.query.filter_by(display_name=user_json['display_name'],followers=user_json['followers']['total']).first():
        
        #update followers if followers are out of date
        target_user.followers = user_json['followers']['total']
        db.session.add(target_user)
        db.session.commit()

    return target_user