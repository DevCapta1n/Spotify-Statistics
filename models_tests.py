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
            display_name = "testing",
            profile_pic_url = "https://www.freeiconspng.com/uploads/icon-user-blue-symbol-people-person-generic--public-domain--21.png"
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

    # def test_top_tracks(self):
    #     """test the TopTrack model"""

    #     tt = TopTrack(
    #         rank = 1,
    #         name = "abc song",
    #         album_cover = "this just needs to be text",
    #         artists = "[{'key':value},{'key':value,'another_key':value_two},{'key':value}]",
    #         user_id = self.uid,
    #         time_range = 'range'
    #     )

    #     db.session.add(tt)
    #     db.session.commit()

    #     self.assertEqual(tt.rank,1)

    # def test_top_artists(self):
    #     """test the TopArtist model"""

    #     ta = TopArtist(
    #         rank = 1,
    #         artist_name = 'Drake',
    #         image = "this just needs to be text",
    #         user_id = self.uid,
    #         time_range = 'forever'
    #     )

    #     db.session.add(ta)
    #     db.session.commit()

    #     self.assertEqual(ta.artist_name, 'Drake')

if __name__ == '__main__':
    unittest.main()