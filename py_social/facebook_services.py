# coding: utf-8
from datetime import datetime, timedelta
import logging
import os
import re
import sys

from dateutil.parser import *
import requests


class FacebookError(Exception): pass

class FacebookConnectionError(FacebookError): pass

class FacebookConnectionLimit(FacebookError): pass

class FacebookDataError(FacebookError): pass

class FacebookPermissionError(FacebookError): pass

class FacebookInvalidId(FacebookError): pass


def get_event_id_from_facebook_url(value):
    return int(re.match(r'.+/events/(?P<fb_id>\d+).*', value).group('fb_id'))

def get_user_id_from_facebook_url(value):
    return int(re.match(r'.+id=(?P<fb_id>\d+).*', value).group('fb_id'))


# http://developers.facebook.com/tools/explorer/
class FacebookGraphApi(object):
    URL = 'https://graph.facebook.com/%(fb_id)s/'
    # http://developers.facebook.com/docs/authentication/
    URL_TOKEN = 'https://graph.facebook.com/oauth/access_token?grant_type=client_credentials&client_id=%(app_id)s&client_secret=%(app_secret)s'

    def __init__(self, fb_id, app_id=None, app_secret=None):
        self.data = {}
        self.fb_id = fb_id
        self.app_id = app_id if app_id else os.environ.get('FACEBOOK_API_KEY', '')
        self.app_secret = app_secret if app_secret else os.environ.get('FACEBOOK_API_SECRET', '')

        self._access_token = None
        self._number_of_requests = 0
        self._timestamp_token_updated = None

    def set_log_level(self, logging_level):
        logging.getLogger().setLevel(logging_level)

    # http://developers.facebook.com/blog/post/2011/05/13/how-to--handle-expired-access-tokens/
    def update_access_token(self):
        token_not_loaded = self._access_token is None
        token_expired = (not self._timestamp_token_updated) or datetime.now() > self._timestamp_token_updated + timedelta(minutes=5)
        too_many_requests = self._number_of_requests % 50 == 0
        if  too_many_requests or token_expired or token_not_loaded:
            url = self.URL_TOKEN % dict(app_id=self.app_id, app_secret=self.app_secret)
            self._access_token = requests.get(url).text
            self._timestamp_token_updated = datetime.now()
        return self._access_token

    def _add_access_token_to_url(self, graph_url):
        if '?' in graph_url:
            return ''.join([graph_url, '&', self._access_token])
        else:
            return ''.join([graph_url, '?', self._access_token])

    def validate_status_code(self, code):
        if code == 401 or code == 403:
            raise FacebookPermissionError('Invalid access token for this action')
        elif code == 404:
            raise FacebookInvalidId('Is the url correct? %s' % self.fb_id)
        elif code == 400: # py-social bug or bad usage of the lib or country/age/etc restriction
            raise FacebookPermissionError('Is your access token valid for this action?')

    def validate_response(self, data):
        error = data.get('error', None)
        if error:
            # {
            #    "error": {
            #       "message": "An access token is required to request this resource.",
            #       "type": "OAuthException",
            #       "code": 104
            #    }
            # }
            code = int(error.get('code'), 0)
            msg = error.get('message', '')
            error_type = error.get('type', '')
            if code == 104 or code == 102 or error_type == 'OAuthException':
                raise FacebookPermissionError('Invalid access token for this action: ' + msg)
            elif code == 17 or code == 4 or code == 613:
                # https://developers.facebook.com/docs/reference/ads-api/api-rate-limiting/
                raise FacebookConnectionLimit('Too many requests to Graph API: ' + msg)
            else:
                raise FacebookError(msg)

    def load_graph(self, graph_url):
        self._number_of_requests += 1
        graph_url = graph_url % dict(fb_id=self.fb_id)
        self.update_access_token()
        graph_url = self._add_access_token_to_url(graph_url)
        logging.info(graph_url)
        headers = {'content-type': 'application/json'}
        r = requests.get(graph_url, headers=headers)
        logging.debug(r)
        self.validate_status_code(r.status_code)
        self.validate_response(r.json())
        return r.json()

    def load(self, **kwargs):
        params = '&'.join([k + '=' + v for k, v in kwargs.items()])
        self.data = self.load_graph(self.URL + '?' + params)
        return self.data

    def load_image(self, graph_url):
        self._number_of_requests += 1
        self.update_access_token()
        graph_url = self._add_access_token_to_url(graph_url)
        logging.info(graph_url)
        r = requests.get(graph_url)
        return r.content

    def parse_timestamp(self, timestamp_str):
        # https://developers.facebook.com/docs/reference/api/dates/
        # Facebook default: ISO8601
        # e.g. 2012-12-15T14:00:02+0000
        return parse(timestamp_str) if timestamp_str else timestamp_str

    def parse_in_naive_timestamp(self, timestamp_str):
        if not timestamp_str:
            return timestamp_str
        t = self.parse_timestamp(timestamp_str)
        format = '%Y-%m-%d %H:%M'
        s = t.strftime(format)
        return datetime.strptime(s, format)

    def format_email(self, email):
        if email:
            return email.replace('\u0040', '@')
        return email


class FacebookUser(FacebookGraphApi):
    "https://developers.facebook.com/docs/reference/api/user/"
    URL = r'https://graph.facebook.com/%(fb_id)s'

    def load(self, fields='email,gender,languages,username,verified', **kwargs):
        return super(FacebookUser, self).load(**kwargs)

    def get_field(self, field):
        if field == 'email':
            return self.get_email()
        return self.data.get(field, None)

    def get_email(self):
        email = self.data.get('email', None)
        username = self.data.get('username', None)
        if not email and username:
            email = '%s@facebook.com' % username
        return self.format_email(email)


class FacebookCommunity(FacebookGraphApi):
    URL_FEED = 'https://graph.facebook.com/%(fb_id)s/feed'

    def __init__(self, fb_id, app_id=None, app_secret=None):
        super(FacebookCommunity, self).__init__(fb_id, app_id=app_id, app_secret=app_secret)
        self.feed = []
        self.next_feed = self.URL_FEED

    def load_feed(self, pages=1):
        if self.has_feed_to_load():
            result = self.load_graph(self.next_feed)
            self.feed += result.get('data', [])
            self.next_feed = result.get('paging', {}).get('next', None)
            if pages > 0:
                self.load_feed(pages=pages-1)
        return self.feed

    def has_feed_to_load(self):
        return self.next_feed is not None

    def get_events_ids_from_feed(self):
        event_ids = []
        for f in self.feed:
            url_re_expression = '.+facebook.com/events/(?P<event_id>\d+).*'
            if 'message' in f:
                try:
                    event_id = re.search(url_re_expression, f['message']).group(1)
                    event_ids.append(int(event_id))
                except AttributeError:
                    pass # not a event link
            if 'link' in f:
                try:
                    event_id = re.search(url_re_expression, f['link']).group(1)
                    event_ids.append(int(event_id))
                except AttributeError:
                    pass # not a event link
        return list(set(event_ids)) # remove replicated links

    def get_recent_users_ids_from_feed(self):
        fb_ids = []
        for f in self.feed:
            if f.get('likes', None):
                fb_ids_from_likes = [l['id'] for l in f['likes']['data']]
                fb_ids += fb_ids_from_likes
            if f.get('comments', None):
                fb_ids_from_comments = [u['from']['id'] for u in f['comments']['data']]
                fb_ids += fb_ids_from_comments
        return list(set(fb_ids))

    def get_all_users_ids(self):
        users = []
        feed_users = self.get_recent_users_ids_from_feed()
        users += feed_users
        return list(set(users))

    def get_all_users(self, fields='email,username', offset=0, limit=5000):
        users = []
        for user_id in self.get_all_users_ids()[offset:limit]:
            fb = FacebookUser(user_id, app_id=self.app_id, app_secret=self.app_secret)
            fb.load(fields=fields)
            fields_splitted = fields.split(',')
            user = dict(fb_id=user_id)
            for f in fields_splitted:
                user[f] = fb.get_field(f)
            users.append(user)
        return users

    def _get_users_ids_from_list(self, result):
        return [u['id'] for u in result]


class FacebookPage(FacebookCommunity):
    "http://developers.facebook.com/docs/reference/api/page/"


class FacebookEvent(FacebookCommunity):
    "https://developers.facebook.com/docs/graph-api/reference/event"
    URL_MAYBE = 'https://graph.facebook.com/%(fb_id)s/maybe'
    URL_ATTENDING = 'https://graph.facebook.com/%(fb_id)s/attending'
    URL_PICTURE = r'https://graph.facebook.com/%(fb_id)s/picture?type=small'
    #http://developers.facebook.com/docs/reference/fql/event/
    URL_ALL_PICTURES = r'https://graph.facebook.com/fql?q=SELECT+pic,pic_big,pic_small+FROM+event+WHERE+eid=%(fb_id)s'

    def __init__(self, fb_id, app_id=None, app_secret=None):
        super(FacebookEvent, self).__init__(fb_id, app_id=app_id, app_secret=app_secret)
        self.maybe = {}
        self.attending = {}
        self.flyer = None
        self.flyers_info = None
        self.flyer_default = None
        self.flyer_big = None
        self.flyer_small = None

    def load_maybe(self):
        self.maybe = self.load_graph(self.URL_MAYBE)
        return self.maybe

    def load_attending(self):
        self.attending = self.load_graph(self.URL_ATTENDING)
        return self.attending

    def load_small_flyer(self):
        self.flyer = self.load_image(self.URL_PICTURE)
        return self.flyer

    def load_flyers(self):
        self.flyers_info = self.load_graph(self.URL_ALL_PICTURES)
        try:
            self.flyer_default = self.load_image(self.flyers_info['data'][0]['pic'])
        except (KeyError, IndexError):
            pass
        try:
            self.flyer_big = self.load_image(self.flyers_info['data'][0]['pic_big'])
        except (KeyError, IndexError):
            pass
        try:
            self.flyer_small = self.load_image(self.flyers_info['data'][0]['pic_small'])
        except (KeyError, IndexError):
            pass
        return self.flyers_info

    def get_recent_users_ids_from_maybe(self):
        return list(set(self._get_users_ids_from_list(self.maybe.get('data', []))))

    def get_recent_users_ids_from_attending(self):
        return list(set(self._get_users_ids_from_list(self.attending.get('data', []))))

    def get_all_users_ids(self):
        users = super(FacebookEvent, self).get_all_users_ids()
        users += self.get_recent_users_ids_from_maybe()
        users += self.get_recent_users_ids_from_attending()
        return list(set(users))

    def get_name(self):
        return self.data.get('name', None)

    def get_owner(self):
        return self.data.get('owner', {}).get('id', None)

    def get_lat_long(self):
        try:
            return self.data['venue']['latitude'], self.data['venue']['longitude']
        except KeyError:
            return None, None

    def get_location(self):
        return self.data.get('location', '')

    def get_timestamp(self):
        return self.parse_timestamp(self.data.get('start_time', None))

    def get_naive_timestamp(self):
        return self.parse_in_naive_timestamp(self.data.get('start_time', None))

    def get_timestamp_str(self):
        return self.get_timestamp().strftime('%Y-%m-%d %H:%M')

    def get_date_str(self):
        return self.get_timestamp().strftime('%Y-%m-%d')

    def get_time_str(self):
        # http://developers.facebook.com/docs/reference/api/
        return self.get_timestamp().strftime('%H:%M')

    def get_flyer(self):
        return self.flyer

    def get_flyer_default(self):
        return self.flyer_default

    def get_flyer_big(self):
        return self.flyer_big

    def get_flyer_small(self):
        return self.flyer_small


class FacebookGroup(FacebookCommunity):
    "http://developers.facebook.com/docs/reference/api/group/"
    URL_MEMBERS = 'https://graph.facebook.com/%(fb_id)s/members'

    def __init__(self, fb_id, app_id=None, app_secret=None):
        super(FacebookGroup, self).__init__(fb_id, app_id=app_id, app_secret=app_secret)
        self.members = {}

    def load_members(self, offset=0, limit=1000): # TODO: offset+limit
        self.members = self.load_graph(self.URL_MEMBERS)
        return self.members

    def get_recent_users_ids_from_members(self):
        return list(set(self._get_users_ids_from_list(self.members.get('data', []))))

    def get_all_users_ids(self):
        users = super(FacebookGroup, self).get_all_users_ids()
        users += self.get_recent_users_ids_from_members()
        return list(set(users))

    def get_email(self):
        "Send e-mail to post in Group's feed"
        return self.format_email(self.data.get('email', None))

    def get_privacy(self):
        return self.data.get('privacy', None)
