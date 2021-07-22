"""Statify models tests"""

import os
from unittest import TestCase
import unittest
from models import db, connect_db, User

os.environ['DATABASE_URL'] = 'postgresql://statify-test'

from app import app

db.create_all()

class StatifyModelTestCase(TestCase):
    """Test models"""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()

        self.uid = 94566
        u = User(
            display_name = "test UN",
            password = "test PW",
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
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_user_dict(self):
        """test if the user to_dict method works"""

        with self.client as c:
            u = self.u
            dictionary = u.to_dict()

            self.assertEqual(dictionary['display_name'], 'test UN')
            self.assertEqual(dictionary['country'], 'US')

if __name__ == '__main__':
    unittest.main()