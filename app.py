from flask import Flask, request, redirect, render_template, flash, session, jsonify
from models import db, connect_db, User
import json
import requests
import base64
from requests.structures import CaseInsensitiveDict
from update_database import update_user

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://dntodqqmwqhnbp:07d80f8160de44f0ef95e54e8a29bb9aa40b50035348368e811975314ecfaff6@ec2-23-23-164-251.compute-1.amazonaws.com:5432/db13kla797kgl4"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'ihaveasecret'

connect_db(app)
db.create_all()

client_id = "7c396993dafd46c3b30341981ec56217"
urlBase = "https://statify-winford.herokuapp.com/"
redirect_uri = urlBase + 'login'

def base_64(text):
    """convert text to ascii decoded base64"""

    text_as_bytes = text.encode('ascii')
    text_as_base64 = base64.b64encode(text_as_bytes)
    return text_as_base64.decode("ascii")

def fix_short_list(art_list, trk_list):
    """if the number of artists or tracks returned by the api is less than
    ten then add an item to the list telling the user they don't have enough
    data"""

    if len(art_list) < 10:
        art_list.append({'images': [{},{},{'url':'/static/images/noDataImg.jpg'}], 'name': 'You do not have ten artists in your history'})
    if len(trk_list) < 10:
        trk_list.append({'album': {'images': [{},{'url':'/static/images/noDataImg.jpg'}]},
                                'name': 'You do not have ten tracks in your history',
                                'artists': [{'name':'no artist'}]})
    return [art_list, trk_list]

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

    return redirect(f"https://accounts.spotify.com/authorize?client_id={client_id}&response_type=code&redirect_uri={redirect_uri}&scope=user-top-read%20user-read-private%20user-read-email")

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

    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/json"
    headers["Content-Type"] = "application/json"
    headers["Authorization"] = f"Bearer {api_token_resp.json()['access_token']}"

    #through a request to the spotify api get the current users profile data
    curr_user = requests.get('https://api.spotify.com/v1/me', headers=headers)
    curr_user = curr_user.json()
    token = api_token_resp.json()['access_token']
    new_user = update_user(curr_user, token)
    session['user'] = new_user.id
    return redirect(f'/statistics-home/{new_user.id}')
    
@app.route('/statistics-home/<user_id>', methods=['POST', 'GET'])
def display_stats(user_id):
    """display the top artists and tracks the given user, also taking into account the 
    time range of their top artists and tracks"""

    artist_range = "long_term"
    track_range = "long_term"
    curr_user = User.query.get_or_404(user_id)

    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/json"
    headers["Content-Type"] = "application/json"
    headers["Authorization"] = f"Bearer {curr_user.token}"

    url = f"https://api.spotify.com/v1/me/top/artists?time_range={artist_range}&limit=10&offset=0"
    track_url = f"https://api.spotify.com/v1/me/top/tracks?time_range={track_range}&limit=10&offset=0"

    #get the top ten artists and tracks for logged in user
    top_artists = requests.get(url, headers=headers)
    t_tracks = requests.get(track_url, headers=headers)

    fixed_lists = fix_short_list(top_artists.json()['items'], t_tracks.json()['items'])
    top_ten_artists = fixed_lists[0]
    top_ten_tracks = fixed_lists[1]

    if request.method == 'POST':

        artist_range = request.form['artist_range']
        track_range = request.form['track_range']

        url = f"https://api.spotify.com/v1/me/top/artists?time_range={artist_range}&limit=10&offset=0"
        track_url = f"https://api.spotify.com/v1/me/top/tracks?time_range={track_range}&limit=10&offset=0"

        #get the top ten artists and tracks for logged in user
        top_artists = requests.get(url, headers=headers)
        t_tracks = requests.get(track_url, headers=headers)

        fixed_lists = fix_short_list(top_artists.json()['items'], t_tracks.json()['items'])
        top_ten_artists = fixed_lists[0]
        top_ten_tracks = fixed_lists[1]
        return render_template('stats.html',
                                artists=top_ten_artists,
                                tracks=top_ten_tracks,
                                art_range=artist_range,
                                trk_range=track_range)

    return render_template('home.html',
                            title=f"{curr_user.display_name}'s Spotify Statistics",
                            artists=top_ten_artists,
                            tracks=top_ten_tracks,
                            user=curr_user,
                            art_range=artist_range,
                            trk_range=track_range)

@app.route('/profile/<user_id>', methods=['POST', 'GET'])
def display_profile(user_id):
    """display the profile page for a user where they can view and edit all the information
    for there account"""

    curr_user = User.query.get_or_404(user_id)
    if request.method == 'POST':

        curr_user.profile_pic_url = request.form['picture'] or curr_user.profile_pic_url
        curr_user.display_name = request.form['username'] or curr_user.display_name
        curr_user.country = request.form['country'] or curr_user.country
        db.session.add(curr_user)
        db.session.commit()
    return render_template('profile.html',
                            user=curr_user)

@app.route('/logout/<user_id>')
def logout(user_id):
    """flash a logout message and redirect to the landing page"""

    curr_user = User.query.get_or_404(user_id)
    flash(f"{curr_user.display_name} has been logged out", 'success')
    return redirect('/')

@app.route('/get-user')
def get_user():
    """return a json representation of the current user's user object"""

    curr_user = User.query.get_or_404(session['user'])
    return jsonify(curr_user.to_dict())