"""Statify app tests"""

import os
import unittest
import base64
import json
from unittest import TestCase
from flask import Flask, session
from app import app, add_un_and_pw, do_login, do_logout, fix_short_list, base_64
from models import db, connect_db, User


os.environ['DATABASE_URL'] = 'postgresql://statify_test'

from app import app

db.create_all()

class StatifyAppTestCase(TestCase):
    """Test App"""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()

        self.uid = 94566
        u = User(
            display_name = "test",
            password = "test",
            profile_pic_url = "https://www.freeiconspng.com/uploads/icon-user-blue-symbol-people-person-generic--public-domain--21.png",
            token = "fakeToken",
            country = "US",
            spotify_link = "google.com",
            followers = 9
        )
        db.session.add(u)
        u.id = self.uid
        db.session.commit()

        self.u = User.query.get(self.uid)

        self.client = app.test_client()

    def tearDown(self):
        resp = super().tearDown()
        db.session.rollback()
        return resp

    def test_add_un_and_pw(self):
        """test adding a username and password to the session"""
        with self.client as c:
            auth_page = c.get('/')
            add_un_and_pw('qwerty','asdfgh')
            self.assertEqual(session['UN'], 'qwerty')
            self.assertFalse(session['PW'] == 'asdfgh')
            self.assertEqual(type(session['PW']), str)

    def test_login_and_logout(self):
        """test the login and logout helper functions"""
        with self.client as c:
            auth_page = c.get('/')
            do_login(self.u)
            self.assertEqual(session['user'], 94566)
            do_logout()
            self.assertFalse('user' in session)

    def test_fix_short_list(self):
        """test the fix_short_list helper function"""
        with self.client as c:
            auth_page = c.get('/')
            artists = []
            tracks = []
            result_array = fix_short_list(artists,tracks)
            self.assertEqual(result_array[0][0],{'images': [{},{},{'url':'/static/images/noDataImg.jpg'}], 'name': 'You do not have ten artists in your history'})
            self.assertEqual(result_array[1][0],{'album': {'images': [{},{'url':'/static/images/noDataImg.jpg'}]},
                                'name': 'You do not have ten tracks in your history',
                                'artists': [{'name':'no artist'}]})
            long_artists = [1,2,3,4,5,6,7,8,9,10,11]
            long_tracks = [1,2,3,4,5,6,7,8,9,10,11]
            result_array = fix_short_list(long_artists,long_tracks)
            self.assertEqual(result_array[0], [1,2,3,4,5,6,7,8,9,10,11])
            self.assertEqual(result_array[1], [1,2,3,4,5,6,7,8,9,10,11])
    
    def test_base_64_encoder(self):
        """test the base_64 helper function by checking if it encodes as expected"""
        with self.client as c:
            auth_page = c.get('/')
            encoded = base_64("this is not an encoded string but it will be base64 soon")
            try:
                self.assertEqual(base64.b64encode(base64.b64decode(encoded)).decode("ascii"),encoded)
            except Exception:
                print("failing the test on purpose if there is an error")
                self.assertTrue(False)

    def test_root(self):
        """test that the root path is displaying the authorize.html page correctly"""
        with self.client as c:
            resp = c.get("/")

            self.assertIn("Welcome to Statify", str(resp.data))
            self.assertIn("sign up", str(resp.data))
            self.assertIn("created by: Jack Winford", str(resp.data))

    def test_signup(self):
        """test signing up and displaying the sign in page"""
        with self.client as c:
            resp = c.get("/signup")
            self.assertEqual(resp.status_code, 200)
            self.assertIn('<label for="username">username</label>', str(resp.data))
            self.assertIn("<span>Signup by creating a username and password</span>", str(resp.data))
            self.assertIn("<span>Make sure to remember your username and password.", str(resp.data))

            resp = c.post("/signup", content_type='multipart/form-data', data={'username':'','password':''})
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Username must contain at least one character", str(resp.data))

            resp = c.post("/signup", content_type='multipart/form-data', data={'username':'unTest','password':'pwTest'})
            self.assertEqual(resp.status_code, 302)

    def test_login(self):
        """test logging in and displaying the login page"""
        with self.client as c:
            resp = c.get("/login")
            self.assertEqual(resp.status_code, 200)
            self.assertIn('<label for="username">username</label>', str(resp.data))
            self.assertIn("<span>Login with your username and password</span>", str(resp.data))

            resp = c.post("/login", content_type='multipart/form-data', data={'username':'','password':''})
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Username must contain at least one character", str(resp.data))

            resp = c.post("/login", content_type='multipart/form-data', data={'username':'unTest','password':'pwTest'})
            self.assertEqual(resp.status_code, 200)

    def test_logout(self):
        """test logging out a user after logging in"""
        with self.client as c:
            resp = c.get("/login", content_type='multipart/form-data', data={'username':'unTest','password':'pwTest'})
            self.assertEqual(resp.status_code, 200)
            resp = c.get("/logout")
            self.assertEqual(resp.status_code, 302)

    def test_authorize(self):
        """test the /authorize routes response when logged in and not logged in"""
        with self.client as c:
            resp = c.get("/login", content_type='multipart/form-data', data={'username':'unTest','password':'pwTest'})
            self.assertEqual(resp.status_code, 200)
            resp = c.get("/authorize")
            self.assertEqual(resp.status_code, 302)

    def test_display_stats(self):
        """test displaying the stats for the test user"""
        with self.client as c:
            with c.session_transaction() as session:
                session['user'] = self.u.id

            try:
                resp = c.get("/statistics-home")
            except Exception:
                #the route throws an error because the current user does not have 
                #an updated token and therefor the first Spotify API requests fail
                self.assertEqual(resp.status_code, 500)

    def test_display_stats(self):
        """test displaying the stats for the test user"""
        with self.client as c:
            with c.session_transaction() as session:
                session['user'] = self.u.id
            
            resp = c.get("/profile")
            self.assertEqual(resp.status_code, 200)
            self.assertIn('target="_blank">View Your Spotify Page</a></li>', str(resp.data))
            self.assertIn('<button class="btn btn-lrg btn-danger" role="button">Delete Account</button>', str(resp.data))
    
    def test_delete_user(self):
        """test the /delete-user route with a logged in user expecting the user to be deleted"""
        with self.client as c:
            with c.session_transaction() as session:
                session['user'] = self.u.id

            user = self.u

            resp = c.post("/delete-user")
            self.assertEqual(resp.status_code, 302)
            self.assertEqual(User.query.get(self.u.id), None)

            #check to see if the correct flask message is being displayed
            auth_page = c.get("/")
            self.assertIn("test&#39;s account has been removed", str(auth_page.data))

            auth_page = c.post("/delete-user")
            self.assertEqual(resp.status_code, 302)
            #check to see if the correct flask message is being displayed
            auth_page = c.get("/")
            self.assertIn("Access unauthorized", str(auth_page.data))

            db.session.add(user)
            db.session.commit()

    def test_get_user(self):
        """test the /get-user route which can return the json representation of a user"""
        with self.client as c:
            with c.session_transaction() as session:
                session['user'] = self.u.id

            resp = c.get("/get-user")
            resp = json.loads(resp.data)
            self.assertEqual(self.u.id, resp["id"])
            self.assertEqual(self.u.spotify_link, resp["spotify_link"])
            self.assertFalse('password' in resp)
    
    def test_get_country_menu(self):
        """test the route which can return the country drop down menu .html file"""
        with self.client as c:
            with c.session_transaction() as session:
                session['user'] = self.u.id

            country_drop_down = c.get("/country-drop-down")
            self.assertEqual(country_drop_down.status_code, 200)
            self.assertIn('<label for="country">Country</label>', str(country_drop_down.data))
            self.assertIn('<option value="Angola">Angola</option>', str(country_drop_down.data))

    def test_getting_405(self):
        """test getting a 405 response on /get-user and /country-drop-down"""
        with self.client as c:
            resp = c.get("/get-user")
            self.assertEqual(resp.status_code, 405)

            resp = c.get("/country-drop-down")
            self.assertEqual(resp.status_code, 405)

if __name__ == '__main__':
    unittest.main()