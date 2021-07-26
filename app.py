from flask import Flask, request, redirect, render_template, flash, session, jsonify, url_for, g, abort
from flask_bcrypt import Bcrypt
app = Flask(__name__)
bcrypt = Bcrypt(app)
from models import db, connect_db, User
import json
import requests
import base64
from requests.structures import CaseInsensitiveDict
from update_database import update_user

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://dntodqqmwqhnbp:07d80f8160de44f0ef95e54e8a29bb9aa40b50035348368e811975314ecfaff6@ec2-23-23-164-251.compute-1.amazonaws.com:5432/db13kla797kgl4"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'ihaveasecret'

connect_db(app)
db.create_all()

client_id = "7c396993dafd46c3b30341981ec56217"
urlBase = "https://statify-winford.herokuapp.com/"

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

def do_login(user):
    """Log in user."""

    session['user'] = user.id

def do_logout():
    """Logout user."""

    if 'user' in session:
        del session['user']

def add_un_and_pw(username, password):
    """Add the username and password from the log in or sign up form 
    to the session"""
    
    hashed = bcrypt.generate_password_hash(password)
    hashed_utf8 = hashed.decode("utf8")

    session['UN'] =  username
    session['PW'] = hashed_utf8

@app.before_request
def add_user_to_g():
    """If the user is logged in, add the current user to Flask global."""

    if 'user' in session:
        g.user = User.query.get(session['user'])
    else:
        g.user = None

@app.route('/')
def root():
    """The root path renders the authorize page."""
    
    return render_template("authorize.html",
                            title="Welcome to Statify")

@app.route('/logout')
def logout():
    """remove the user from the session then flash a logout message 
    and redirect to the landing page"""

    if g.user:
        flash(f"{g.user.display_name} has been logged out", 'success')

    do_logout()
    
    return redirect('/')

@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user sign up.

    Add new username and password to session. Redirect to /authorize route.

    If form not valid, present form.

    If the there already is a user with that username: flash message
    and re-present form.
    """

    if request.method == "POST":

        username = request.form['username']
        password = request.form['password']
        if username == '' or len(username) > 10:
            flash("Username must contain at least one character and be less than ten characters", 'danger')
            return render_template('login.html',
                        form_url = 'signup')
        if password == '' or len(password) > 10:
            flash("Password must contain at least one character and be less than ten characters", 'danger')
            return render_template('login.html',
                        form_url = 'signup')
        if User.query.filter_by(display_name=username).first():
            flash("Username already taken", 'danger')
            return render_template('login.html',
                            form_url = 'signup')
        add_un_and_pw(username, password)
        session['signing in'] = True
        return redirect("/authorize")

    return render_template('login.html',
                            form_url = 'signup')


@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login. Initially display the login page on GET and handle
    the form data on a POST request as a primary authentication function. Redirect
    to the /authorize route when username and password are legitmate"""

    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        if username == '':
            flash("Username must contain at least one character", 'danger')
        if password == '':
            flash("Password must contain at least one character", 'danger')
        user = User.authenticate(request.form['username'],
                                request.form['password'])

        if user:
            add_un_and_pw(username,password)
            do_login(user)
            return redirect("/authorize")

        flash("Invalid credentials.", 'danger')

    return render_template('login.html',
                            form_url = 'login')

@app.route('/authorize', methods=['POST', 'GET'])
def authorize():
    """when the either the /login or /signup routes redirect here, then send
    a request to the authorize end of the Spotify API accounts service"""

    if 'PW' in session:
        redirect_uri = urlBase + 'initialize'
        session['from_authorize'] = True
        return redirect(f"https://accounts.spotify.com/authorize?client_id={client_id}&response_type=code&redirect_uri={redirect_uri}&scope=user-top-read%20user-read-private")

    flash("You must log in before being authorized", 'danger')
    return redirect('/')

@app.route('/initialize', methods=['POST', 'GET'])
def initialize():
    """after redirection from the authorize function handle the user's
    response to the spotify authorization page. As well as create/update
    a user, handle any errors, and finally redirect to /statistics-home"""

    if session['from_authorize'] == True:
        session['from_authorize'] = False
    else:
        redirect('/authorize')

    redirect_uri = urlBase + 'initialize'
    auth_code = request.args.get('code')

    token_form = {}
    token_form["code"] = auth_code
    token_form["redirect_uri"] = redirect_uri
    token_form["grant_type"] = "authorization_code"

    # the client id and secret are combined in base64 encoded text for
    # the authorization 
    client_secret = base_64("7c396993dafd46c3b30341981ec56217:ab3856d0c15b49fea1c56a467ac28605")
    auth_header = CaseInsensitiveDict()
    auth_header["Authorization"] = f"Basic {client_secret}"

    # this request should return an access and refresh token for
    # the authorized user
    token_url = "https://accounts.spotify.com/api/token"
    api_token_resp = requests.post(token_url, headers=auth_header, data=token_form, json=True)

    try:
        api_token_resp.json()['access_token']
    except (json.decoder.JSONDecodeError, KeyError):
        flash("There was an issue communicating with Spotify. Please try again.", "danger")
        return redirect('/')
    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/json"
    headers["Content-Type"] = "application/json"
    headers["Authorization"] = f"Bearer {api_token_resp.json()['access_token']}"

    #through a request to the spotify api get the current users profile data
    curr_user = requests.get('https://api.spotify.com/v1/me', headers=headers)

    try:
        curr_user = curr_user.json()
    except json.decoder.JSONDecodeError:
        flash("There was an issue communicating with Spotify. Please try again.", 'danger')
        return redirect('/')

    if 'signing in' in session and User.query.filter_by(spotify_link=curr_user['external_urls']['spotify']).first():
        #if the user is trying to sign in but their is already an account with their 
        #Spotify data then redirect them to the login
        flash("Your Spotify data is already on an account and the username you entered does not exist", "danger")
        del session['signing in']
        return render_template('login.html',
                        form_url = 'login')

    if 'signing in' in session:
        del session['signing in']

    #create/update the user as well as log them into the session
    token = api_token_resp.json()['access_token']
    new_user = update_user(curr_user, session['UN'], session['PW'], token)
    do_login(new_user)

    del session['UN']
    del session['PW']
    return redirect('/statistics-home')

@app.route('/statistics-home', methods=['POST', 'GET'])
def display_stats():
    """display the top artists and tracks the given user, also taking into account the 
    time range of their top artists and tracks"""
    pages = {'one': 0, 'two': 10, 'three': 20, 'four': 30, 'five': 40}

    if g.user == None:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    curr_user = g.user

    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/json"
    headers["Content-Type"] = "application/json"
    headers["Authorization"] = f"Bearer {curr_user.token}"

    if request.method == 'POST':

        if 'use_session' in request.json:
            offset = pages[request.json['page']]
        else:
            offset = 0
            session['artist_range'] = request.json['artist_range']
            session['track_range'] = request.json['track_range']

        url = f"https://api.spotify.com/v1/me/top/artists?time_range={session['artist_range']}&limit=10&offset={offset}"
        track_url = f"https://api.spotify.com/v1/me/top/tracks?time_range={session['track_range']}&limit=10&offset={offset}"

        #get the top ten artists and tracks for logged in user
        top_artists = requests.get(url, headers=headers)
        t_tracks = requests.get(track_url, headers=headers)

        try:
            fixed_lists = fix_short_list(top_artists.json()['items'], t_tracks.json()['items'])
        except KeyError:
            flash("Your session with spotify ended. Log back in to start a new session", "warning")
            return redirect("/login")

        top_ten_artists = fixed_lists[0]
        top_ten_tracks = fixed_lists[1]
        return render_template('stats.html',
                                artists=top_ten_artists,
                                tracks=top_ten_tracks,
                                offset=offset,
                                art_range=session['artist_range'],
                                trk_range=session['track_range'])

    session['artist_range'] = "long_term"
    session['track_range'] = "long_term"

    url = f"https://api.spotify.com/v1/me/top/artists?time_range={session['artist_range']}&limit=10&offset=0"
    track_url = f"https://api.spotify.com/v1/me/top/tracks?time_range={session['track_range']}&limit=10&offset=0"

    #get the top ten artists and tracks for logged in user
    top_artists = requests.get(url, headers=headers)
    t_tracks = requests.get(track_url, headers=headers)

    try:
        fixed_lists = fix_short_list(top_artists.json()['items'], t_tracks.json()['items'])
    except KeyError:
        flash("Your session with spotify ended. Log back in to start a new session", "warning")
        return redirect("/login")

    
    
    top_ten_artists = fixed_lists[0]
    top_ten_tracks = fixed_lists[1]
    return render_template('home.html',
                            title=f"{curr_user.display_name}'s Spotify Statistics",
                            artists=top_ten_artists,
                            tracks=top_ten_tracks,
                            user=curr_user,
                            art_range=session['artist_range'],
                            trk_range=session['track_range'])

@app.route('/profile', methods=['POST', 'GET'])
def display_profile():
    """display the profile page for a user where they can view and edit all the information
    for there account"""

    if g.user == None:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    curr_user = g.user

    if request.method == 'POST':

        curr_user.profile_pic_url = request.form['picture']
        curr_user.display_name = request.form['username']
        curr_user.country = request.form['country']
        db.session.add(curr_user)
        db.session.commit()

    return render_template('profile.html',
                            user=curr_user)

@app.route('/delete-user', methods=['POST'])
def delete_user():
    """remove the logged in user from the session and database"""

    if g.user == None:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    curr_user = User.query.filter_by(id=session['user']).one()
    do_logout()
    flash(f"{curr_user.display_name}'s account has been removed", 'success')

    db.session.delete(curr_user)
    db.session.commit()
    
    return redirect('/')

@app.route('/get-user')
def get_user():
    """return the json representation of a user or abort if the user
    does not exist"""

    if g.user:
        curr_user = g.user
        return jsonify(curr_user.to_dict())

    abort(405)

@app.route('/country-drop-down')
def get_menu():
    """return the HTML file with the country drop down menu. Abort if
    there is not an authorized user in the session"""

    if g.user:
        return render_template('countrydropdown.html',
                                currCountry=g.user.country)

    abort(405)