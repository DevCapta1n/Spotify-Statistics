"""functions for updating the statify database with data from the spotify api"""

from models import db, connect_db, User

def update_user(user_json, token):
    """update, create, or do nothing, then return the passed in user"""

    target_user = User.query.filter_by(display_name=user_json['external_urls']['spotify']).first()

    if not target_user:
        try:
            #some responses may include a country key and value pair
            country = user_json['country']
        except KeyError:
            country = 'US'

        #procede if the target_user does not exist in the database
        new_user = User(
            display_name = user_json['display_name'],
            profile_pic_url = user_json['images'][0]['url'],
            token = token,
            country = country,
            spotify_link = user_json['external_urls']['spotify'],
            followers = user_json['followers']['total']
        )
        db.session.add(new_user)
        db.session.commit()

        return new_user

    if not User.query.filter_by(token=token).first():

        #an existing user's token should be out of date every session
        #so it needs to be updated
        target_user.token = token
        db.session.add(target_user)
        db.session.commit()

    if not User.query.filter_by(display_name=user_json['external_urls']['spotify'],followers=user_json['followers']['total']).first():
        
        target_user.followers = user_json['followers']['total']
        db.session.add(target_user)
        db.session.commit()

    return target_user