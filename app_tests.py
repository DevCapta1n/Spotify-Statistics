"""Statify app tests"""

import os
from unittest import TestCase
import unittest
from app import app
# from flask import Flask
# from flask_bcrypt import Bcrypt
# app = Flask(__name__)
# bcrypt = Bcrypt(app)
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
            followers = 9,
            new = True
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

    def test_root(self):
        """test that the root path is displaying the authorize.html page correctly"""
        with self.client as c:
            resp = c.get("/")

            self.assertIn("Welcome to Statify", str(resp.data))
            self.assertIn("login with Spotify", str(resp.data))
            self.assertIn("created by: Jack Winford", str(resp.data))

    def test_login(self):
        """test logging in and displaying the login page"""
        with self.client as c:
            resp = c.get("/login")

if __name__ == '__main__':
    unittest.main()