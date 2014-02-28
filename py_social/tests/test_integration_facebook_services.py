from datetime import datetime
import os
import unittest

from ..facebook_services import *

# export TEST_FB_USER=1392965554
# export TEST_FB_EVENT=574531142642166
# export TEST_FB_PAGE=627676453946073
# export TEST_FB_GROUP=
# export TEST_FB_APP_ID=
# export TEST_FB_APP_SECRET=
class FacebookTestCase(unittest.TestCase):
    user_id = os.getenv('TEST_FB_USER')
    event_id = os.getenv('TEST_FB_EVENT')
    page_id = os.getenv('TEST_FB_PAGE')
    group_id = os.getenv('TEST_FB_GROUP')
    app_id = os.getenv('TEST_FB_APP_ID')
    app_secret = os.getenv('TEST_FB_APP_SECRET')
    FB_CLASS = FacebookGraphApi
    fb_id = ''

    def setUp(self):
        super(FacebookTestCase, self).setUp()
        self.fb = self.FB_CLASS(self.fb_id, app_id=self.app_id, app_secret=self.app_secret)
        self.fb.load()


class FacebookUserInfoTests(FacebookTestCase):
    FB_CLASS = FacebookUser
    fb_id = FacebookTestCase.user_id

    def test_get_info(self):
        self.assertEquals('1392965554', self.fb.get_field('id'))
        self.assertEquals('male', self.fb.get_field('gender'))
        self.assertEquals('paulocheque@gmail.com', self.fb.get_field('email'))


class FacebookCommunityTests(FacebookTestCase):
    FB_CLASS = FacebookCommunity
    fb_id = FacebookTestCase.group_id # to avoid errors of empty id

    def setUp(self):
        super(FacebookCommunityTests, self).setUp()
        self.fb.load_feed()

    def test_get_events_ids_from_feed(self):
        fb_ids = self.fb.get_events_ids_from_feed()
        self.assertEquals(True, len(fb_ids) >= 0)

    def test_get_recent_users_ids_from_feed(self):
        fb_ids = self.fb.get_recent_users_ids_from_feed()
        self.assertEquals(True, len(fb_ids) >= 0)

    def test_get_all_users_ids(self):
        fb_ids = self.fb.get_all_users_ids()
        self.assertEquals(True, len(fb_ids) >= 0)

    def test_get_all_users(self):
        users = self.fb.get_all_users(limit=1)
        self.assertEquals(True, len(users) >= 0)


class FacebookEventTests(FacebookCommunityTests):
    FB_CLASS = FacebookEvent
    fb_id = FacebookTestCase.event_id

    def test_get_name(self):
        r = u"3\xba Ato contra a Copa 'Se n\xe3o tiver transporte n\xe3o vai ter Copa!'"
        self.assertEquals(r, self.fb.get_name())

    def test_get_location(self):
        self.assertEquals(u'Largo Da Batata', self.fb.get_location())

    def test_get_timestamp(self):
        self.assertEquals('2014-03-13 18:00', self.fb.get_timestamp().strftime('%Y-%m-%d %H:%M'))

    def test_get_naive_timestamp(self):
        self.assertEquals(datetime(2014, 03, 13, 18, 00, 00), self.fb.get_naive_timestamp())

    def test_get_date_str(self):
        self.assertEquals('2014-03-13', self.fb.get_date_str())

    def test_get_time_str(self):
        self.assertEquals('18:00', self.fb.get_time_str())

    def test_maybe(self):
        self.fb.load_maybe()
        self.fb.get_recent_users_ids_from_maybe()

    def test_attending(self):
        self.fb.load_attending()
        self.fb.get_recent_users_ids_from_attending()

    def test_small_flyer(self):
        self.fb.load_small_flyer()
        self.fb.get_flyer()

    def test_flyers(self):
        self.fb.load_flyers()
        self.fb.get_flyer_default()
        self.fb.get_flyer_big()
        self.fb.get_flyer_small()


class FacebookGroupTests(FacebookCommunityTests):
    FB_CLASS = FacebookGroup
    fb_id = FacebookTestCase.group_id

    def test_email(self):
        self.assertEquals('606388089437098@groups.facebook.com', self.fb.get_email())

    def test_get_privacy(self):
        self.assertEquals('OPEN', self.fb.get_privacy())

    def test_get_recent_users_ids_from_members(self):
        self.fb.load_members()
        fb_ids = self.fb.get_recent_users_ids_from_members()


class FacebookPageTests(FacebookCommunityTests):
    FB_CLASS = FacebookPage
    fb_id = FacebookTestCase.page_id

