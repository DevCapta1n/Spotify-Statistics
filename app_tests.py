"""Statify app tests"""

import os
from unittest import TestCase
import unittest
from models import db, connect_db, User, TopArtist, TopTrack

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
            profile_pic_url = "https://www.freeiconspng.com/uploads/icon-user-blue-symbol-people-person-generic--public-domain--21.png"
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
            self.assertIn("Login with Spotify", str(resp.data))
            self.assertIn("Created By: Jack Winford", str(resp.data))

    def test_stats_home(self):
        """test that the /statistics-home page is displaying the home page correctly"""
        with self.client as c:
            resp = c.get("/statistics-home/94566")

            self.assertIn("test_user", str(resp.data))
            self.assertIn("Select A Time Range for Artists", str(resp.data))
            self.assertIn("Statify", str(resp.data))

if __name__ == '__main__':
    unittest.main()