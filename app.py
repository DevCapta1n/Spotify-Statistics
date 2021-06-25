from flask import Flask, request, redirect, render_template
from models import db, connect_db, User, Recommendation
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

    return render_template('home.html',
                            title="Your Spotify Statistics",
                            artists=top_ten_artists,
                            tracks=top_ten_tracks)