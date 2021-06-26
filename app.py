from flask import Flask, request, redirect, render_template
from models import db, connect_db, User, TopArtist, TopTrack
import json
import requests
import base64
from requests.structures import CaseInsensitiveDict

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///statify"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'ihaveasecret'

connect_db(app)
db.create_all()

client_id = "7c396993dafd46c3b30341981ec56217"
urlBase = "http://127.0.0.1:5000/"
redirect_uri = urlBase + 'login'

def base_64(text):
    text_as_bytes = text.encode('ascii')
    text_as_base64 = base64.b64encode(text_as_bytes)
    return text_as_base64.decode("ascii")

@app.route('/')
def root():
    """The root path renders the authorize page."""

    return render_template("authorize.html",
                            title="Welcome to Statify")

@app.route('/authorize', methods=['POST', 'GET'])
def authorize():
    """when the user clicks on the login butten send a request to the authorize
    end of the Spotify API accounts service"""

    redirect_uri = urlBase + 'login'

    return redirect(f"https://accounts.spotify.com/authorize?client_id={client_id}&response_type=code&redirect_uri={redirect_uri}&scope=user-top-read")

@app.route('/login', methods=['POST', 'GET'])
def login():
    """after redirection from the authorize function handle the users
    response to the spotify authorization page"""

    client_secret = base_64("7c396993dafd46c3b30341981ec56217:ab3856d0c15b49fea1c56a467ac28605")
    auth_code = request.args.get('code')
    
    token_form = {}
    token_form["code"] = auth_code
    token_form["redirect_uri"] = redirect_uri
    token_form["grant_type"] = "authorization_code"

    # the client id and secret are combined in base64 encoded text for the authorization 
    auth_header = CaseInsensitiveDict()
    auth_header["Authorization"] = f"Basic {client_secret}"

    # this request should return an access and refresh token for the authorized user
    token_url = "https://accounts.spotify.com/api/token"
    api_token_resp = requests.post(token_url, headers=auth_header, data=token_form, json=True)

    url = "https://api.spotify.com/v1/me/top/artists?time_range=long_term&limit=10&offset=0"
    track_url = "https://api.spotify.com/v1/me/top/tracks?time_range=long_term&limit=10&offset=0"
    
    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/json"
    headers["Content-Type"] = "application/json"
    headers["Authorization"] = f"Bearer {api_token_resp.json()['access_token']}"

    top_artists = requests.get(url, headers=headers)
    top_songs = requests.get(track_url, headers=headers)
    
    top_ten_artists = top_artists.json()['items']
    top_ten_tracks = top_songs.json()['items']

    curr_user = requests.get('https://api.spotify.com/v1/me', headers=headers)
    curr_user = curr_user.json()
    print("///////////////////////////////////////")
    print(curr_user)
    print("///////////////////////////////////////")
    print(curr_user['images'])
    print("///////////////////////////////////////")
    print(type(curr_user['images'][0]))
    print("///////////////////////////////////////")
    print(curr_user['images'][0]['url'])
    print("///////////////////////////////////////")
    print(type(curr_user['images']))
    print("///////////////////////////////////////")
    new_user = User(
        display_name = curr_user['display_name'],
        profile_pic_url = curr_user['images'][0]['url']
    )
    # new_user = User(
    #     display_name = "test_user",
    #     profile_pic_url = "https://www.freeiconspng.com/uploads/icon-user-blue-symbol-people-person-generic--public-domain--21.png"
    # )
    db.session.add(new_user)
    db.session.commit()

    for artist in top_ten_artists:
        top_artist = TopArtist(
            rank = top_ten_artists.index(artist),
            artist_name = artist['name'],
            image = artist['images'][2]['url'],
            user_id = new_user.id
        )
        db.session.add(top_artist)
    db.session.commit()
    
    for track in top_ten_tracks:
        print(track)
        print("///////////////////////////////////////")
        top_track = TopTrack(
            rank = top_ten_tracks.index(track),
            name = track['name'],
            album_cover = track['album']['images'][2]['url'],
            artists = track['artists'],
            user_id = new_user.id
        )
        db.session.add(top_track)
    db.session.commit()
    
    return render_template('home.html',
                            title="Your Spotify Statistics",
                            artists=top_ten_artists,
                            tracks=top_ten_tracks)

# soemthing = {'album': 
# {'album_type': 'ALBUM',
# 'artists': 
# [{'external_urls': 
# {'spotify': 'https://open.spotify.com/artist/56ZTgzPBDge0OvCGgMO3OY'}, 
# 'href': 'https://api.spotify.com/v1/artists/56ZTgzPBDge0OvCGgMO3OY', 
# 'id': '56ZTgzPBDge0OvCGgMO3OY', 
# 'name': 'Beach House', 
# 'type': 'artist', 
# 'uri': 'spotify:artist:56ZTgzPBDge0OvCGgMO3OY'}], 
# 'available_markets': [], 
# 'external_urls': {'spotify': 'https://open.spotify.com/album/35vTE3hx3AAXtM6okpJIIt'}, 
# 'href': 'https://api.spotify.com/v1/albums/35vTE3hx3AAXtM6okpJIIt', 
# 'id': '35vTE3hx3AAXtM6okpJIIt', 
# 'images': [{'height': 640, 'url': 'https://i.scdn.co/image/ab67616d0000b273fc685af465876c629ad111ef', 
# 'width': 640}, 
# {'height': 300, 
# 'url': 'https://i.scdn.co/image/ab67616d00001e02fc685af465876c629ad111ef', 
# 'width': 300}, 
# {'height': 64, 
# 'url': 'https://i.scdn.co/image/ab67616d00004851fc685af465876c629ad111ef', 
# 'width': 64}], 
# 'name': 'Depression Cherry', 
# 'release_date': '2015-08-28', 
# 'release_date_precision': 'day', 
# 'total_tracks': 9, 'type': 'album', 
# 'uri': 'spotify:album:35vTE3hx3AAXtM6okpJIIt'}, 
# 'artists': [{'external_urls': {'spotify': 'https://open.spotify.com/artist/56ZTgzPBDge0OvCGgMO3OY'},
# 'href': 'https://api.spotify.com/v1/artists/56ZTgzPBDge0OvCGgMO3OY', 
# 'id': '56ZTgzPBDge0OvCGgMO3OY', 
# 'name': 'Beach House', 
# 'type': 'artist', 
# 'uri': 'spotify:artist:56ZTgzPBDge0OvCGgMO3OY'}], 
# 'available_markets': [], 
# 'disc_number': 1, 
# 'duration_ms': 320466, 
# 'explicit': False, 
# 'external_ids': {'isrc': 'USSUB1512203'}, 
# 'external_urls': {'spotify': 'https://open.spotify.com/track/0hNhlwnzMLzZSlKGDCuHOo'}, 
# 'href': 'https://api.spotify.com/v1/tracks/0hNhlwnzMLzZSlKGDCuHOo', 
# 'id': '0hNhlwnzMLzZSlKGDCuHOo', 
# 'is_local': False, 
# 'name': 'Space Song', 
# 'popularity': 3, 
# 'preview_url': None, 
# 'track_number': 3, 
# 'type': 'track', 
# 'uri': 'spotify:track:0hNhlwnzMLzZSlKGDCuHOo'}
