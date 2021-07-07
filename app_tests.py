"""Statify app tests"""

import os
from unittest import TestCase
import unittest
from models import db, connect_db, User

os.environ['DATABASE_URL'] = 'postgresql://statify-test'

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
            display_name = "test_user",
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

    def test_root(self):
        """test that the root path is displaying the authorize.html page correctly"""
        with self.client as c:
            resp = c.get("/")

            self.assertIn("Welcome to Statify", str(resp.data))
            self.assertIn("login with Spotify", str(resp.data))
            self.assertIn("created by: Jack Winford", str(resp.data))

if __name__ == '__main__':
    unittest.main()