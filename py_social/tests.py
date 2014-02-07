# coding: utf-8
import unittest

from py_social import *
from py_social.facebook_services import FacebookGraphAPI, FacebookEventPage, FacebookGroupPage, FacebookUserInfo
from py_social.twitter_services import tweet

class FacebookTests(unittest.TestCase):
    def test_x(self):
        FacebookGraphAPI('1', '1', '1', '1')
        FacebookEventPage('1', '1', '1', '1')
        FacebookGroupPage('1', '1', '1', '1')
        FacebookUserInfo('1', '1', '1', '1')
        self.assertEquals(True, True)


class TwitterTests(unittest.TestCase):
    def test_x(self):
        tweet('')
        self.assertEquals(True, True)
