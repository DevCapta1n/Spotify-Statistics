"""functions for updating the statify database with data from the spotify api"""

from models import db, connect_db, User, TopArtist, TopTrack

def update_user(user_json):
    """update, create, or do nothing, then return the passed in user"""

    target_user = User.query.filter_by(display_name=user_json['display_name']).first()

    if not target_user:

        #procede if the target_user does not exist in the database
        new_user = User(
            display_name = user_json['display_name'],
            profile_pic_url = user_json['images'][0]['url']
        )
        db.session.add(new_user)
        db.session.commit()

        return new_user

    if not User.query.filter_by(profile_pic_url=user_json['images'][0]['url']).first():

        #if the user exists but their profile picture is out of date, update it
        target_user.profile_pic_url = user_json['images'][0]['url']

    return target_user

def update_top_artists(artists, new_user, rainge):
    """accepting a list of artist data in json format update the top_artists table accordingly"""

    for artist in artists:

        database_artist = TopArtist.query.filter_by(artist_name = artist['name'], user_id = new_user.id, time_range = rainge).first()

        top_artist = TopArtist(
            rank = artists.index(artist) + 1,
            artist_name = artist['name'],
            image = artist['images'][2]['url'],
            user_id = new_user.id,
            time_range = rainge
        )
        
        if database_artist:
            if top_artist.rank != database_artist.rank or top_artist.image != database_artist.image:

                #If the json response artist already exists in the database for the given user
                #and is not equal to the response artist, then replace the database artist with
                #the json response artist.
                db.session.delete(database_artist)
                db.session.add(top_artist)
                db.session.commit()
        else:
            db.session.add(top_artist)
            db.session.commit()

    

def update_top_tracks(tracks, new_user, rainge):
    """accepting a list of track data in json format update the top_tracks table accordingly"""

    for track in tracks:

        d_trk = TopTrack.query.filter_by(name = track['name'], user_id = new_user.id, time_range = rainge).first()

        t_trk = TopTrack(
            rank = tracks.index(track) + 1,
            name = track['name'],
            album_cover = track['album']['images'][1]['url'],
            artists = track['artists'],
            user_id = new_user.id,
            time_range = rainge
        )

        if d_trk:
            if t_trk.rank != d_trk.rank or t_trk.album_cover != d_trk.album_cover or t_trk.artists != d_trk.artists:

                #if d_trk exists and it is not a copy of t_trk, update it
                db.session.delete(d_trk)
                db.session.add(t_trk)
                db.session.commit()
        else:
            db.session.add(t_trk)
            db.session.commit()