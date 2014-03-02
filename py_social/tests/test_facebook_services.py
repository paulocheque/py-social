import json
import os
import unittest

from ..facebook_services import *


class FacebookTestCase(unittest.TestCase):
    FB_CLASS = FacebookGraphApi
    FACEBOOK_JSON = """
    {}
    """

    def setUp(self):
        self.fb = self.FB_CLASS(123)
        self.fb.load_graph = lambda url: json.loads(self.FACEBOOK_JSON)
        self.fb.load()


class FacebookUserTests(FacebookTestCase):
    FB_CLASS = FacebookUser
    FACEBOOK_JSON = """
    {
        "id": "123",
        "username": "paulocheque"
    }
    """

    def test_get_field(self):
        self.assertEquals('123', self.fb.get_field('id'))
        self.assertEquals('paulocheque', self.fb.get_field('username'))
        self.assertEquals('paulocheque@facebook.com', self.fb.get_field('email'))


class FacebookCommunityTests(FacebookTestCase):
    FB_CLASS = FacebookCommunity
    FACEBOOK_JSON_FEED = """
    {
        "data": [
            {
                "id":123,
                "message": "http://facebook.com/events/123",
                "likes": {
                    "data": [
                        {"id":1},{"id":2}
                    ]
                },
                "comments": {
                    "data": [
                        {"from": {"id":1}},
                        {"from": {"id":3}}
                    ]
                }
            },
            {
                "id":456,
                "link": "http://facebook.com/events/456",
                "likes": {
                    "data": [
                        {"id":1},{"id":2}
                    ]
                },
                "comments": {
                    "data": [
                        {"from": {"id":1}},
                        {"from": {"id":3}}
                    ]
                }
            }
        ],
        "paging": {
          "next": "http://next-url",
          "previous": "http://previous-url"
        }
    }
    """
    FACEBOOK_JSON2 = """
    {
       "data": [

       ]
    }
    """

    def setUp(self):
        super(FacebookCommunityTests, self).setUp()
        self.fb.load_graph = lambda url: json.loads(self.FACEBOOK_JSON_FEED)
        self.fb.load_feed()

    def test_get_events_ids_from_feed(self):
        fb_ids = self.fb.get_events_ids_from_feed()
        self.assertEquals(2, len(fb_ids))
        self.assertEquals(123, fb_ids[1])
        self.assertEquals(456, fb_ids[0])

    def test_get_recent_users_ids_from_feed(self):
        fb_ids = self.fb.get_recent_users_ids_from_feed()
        self.assertEquals(3, len(fb_ids))

    def test_get_all_users_ids(self):
        fb_ids = self.fb.get_all_users_ids()
        self.assertEquals(3, len(fb_ids))

    # def test_get_all_users(self):
    #     self.fb.get_all_users(fields='id')

    def test_has_feed_to_load(self):
        self.fb.load_graph = lambda url: json.loads(self.FACEBOOK_JSON2)
        self.assertEquals(True, self.fb.has_feed_to_load())
        self.fb.load_feed()
        self.assertEquals(False, self.fb.has_feed_to_load())


class FacebookEventTests(FacebookTestCase):
    FB_CLASS = FacebookEvent
    FACEBOOK_JSON = """
    {
       "id": "EVENT ID",
       "owner": {
          "name": "USER NAME",
          "id": "USER ID"
       },
       "name": "NAME",
       "description": "EVENT DESCRIPTION",
       "start_time": "2010-03-14T14:00:00",
       "end_time": "2010-03-14T17:30:00",
       "location": "EVENT LOCATION",
       "venue": {
          "street": "409 Colorado St.",
          "city": "Austin",
          "state": "Texas",
          "country": "United States",
          "latitude": 30.2669,
          "longitude": -97.7428
       },
       "privacy": "OPEN",
       "updated_time": "2010-04-13T15:29:40+0000"
    }
    """
    FACEBOOK_JSON_MAYBE_ATTENDING = """
    {
        "data": [
            {"id":123},
            {"id":456}
        ]
    }
    """

    def test_get_name(self):
        self.assertEquals('NAME', self.fb.get_name())

    def test_get_location(self):
        self.assertEquals('EVENT LOCATION', self.fb.get_location())

    def test_get_date_str(self):
        self.assertEquals('2010-03-14', self.fb.get_date_str())

    def test_get_time_str(self):
        self.assertEquals('14:00', self.fb.get_time_str())

    def test_get_lat_long(self):
        self.assertEquals((30.2669, -97.7428), self.fb.get_lat_long())

    def test_maybe(self):
        self.fb.load_graph = lambda url: json.loads(self.FACEBOOK_JSON_MAYBE_ATTENDING)
        self.fb.load_maybe()
        fb_ids = self.fb.get_recent_users_ids_from_maybe()
        self.assertEquals(2, len(fb_ids))

    def test_attending(self):
        self.fb.load_graph = lambda url: json.loads(self.FACEBOOK_JSON_MAYBE_ATTENDING)
        self.fb.load_attending()
        fb_ids = self.fb.get_recent_users_ids_from_attending()
        self.assertEquals(2, len(fb_ids))


class FacebookGroupTests(FacebookTestCase):
    FB_CLASS = FacebookGroup
    FACEBOOK_JSON = """
    {
       "email": "group@groups.facebook.com",
       "privacy": "OPEN"
    }
    """
    FACEBOOK_JSON_MEMBERS = """
    {
       "data": [
          {
             "name": "PySocial1",
             "administrator": true,
             "id": "123"
          },
          {
             "name": "PySocial2",
             "administrator": true,
             "id": "456"
          }
       ],
       "paging": {
          "next": "https://graph.facebook.com/123/members?limit=100&offset=100"
       }
    }
    """

    def test_email(self):
        self.assertEquals('group@groups.facebook.com', self.fb.get_email())

    def test_get_privacy(self):
        self.assertEquals('OPEN', self.fb.get_privacy())

    def test_get_recent_users_ids_from_members(self):
        self.fb.load_graph = lambda url: json.loads(self.FACEBOOK_JSON_MEMBERS)
        self.fb.load_members()
        fb_ids = self.fb.get_recent_users_ids_from_members()


class FacebookPageTests(FacebookTestCase):
    FB_CLASS = FacebookPage
    FACEBOOK_JSON = """
    {
       "data": [

       ]
    }
    """
