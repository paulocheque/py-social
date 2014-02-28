# coding: utf-8
import logging
import os

import tweepy

# https://github.com/tweepy/tweepy
# https://dev.twitter.com/docs
# https://dev.twitter.com/apps/ID/show


def tweet(message, consumer_key=None, consumer_secret=None, access_token=None, access_token_secret=None, debug=False):
    consumer_key = os.environ.get('TWITTER_CONSUMER_KEY', consumer_key)
    consumer_secret = os.environ.get('TWITTER_CONSUMER_SECRET', consumer_secret)
    access_token = os.environ.get('TWITTER_ACCESS_TOKEN', access_token)
    access_token_secret = os.environ.get('TWITTER_ACCESS_TOKEN_SECRET', access_token_secret)
    if not debug:
        try:
            #authenticator = tweepy.auth.BasicAuthHandler(TWITTER_USERNAME, TWITTER_PASSWORD)
            authenticator = tweepy.auth.OAuthHandler(consumer_key, consumer_secret)
            authenticator.set_access_token(access_token, access_token_secret)

            api = tweepy.API(authenticator)

            api.update_status(message[0:140])
        except Exception as e:
            logging.error(u'Fail to tweet: %s' % message)
            # We do not want to interrupt the application because a tweet error.
