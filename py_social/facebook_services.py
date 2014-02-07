# coding: utf-8
from datetime import datetime, timedelta
import json
import logging
import os
import re
import sys
import urllib2

from .http_services import request


FB_EVENT_URL = r'http://facebook.com/events/%s'
FB_EVENT_GRAPH = r'https://graph.facebook.com/%s?date_format=d/m/Y-H:i&access_token=%s'
FB_EVENT_PICTURE_GRAPH = r'https://graph.facebook.com/%s/picture?type=small&access_token=%s'
#http://developers.facebook.com/docs/reference/fql/event/
FB_EVENT_ALL_PICTURES_GRAPH = r'https://graph.facebook.com/fql?q=SELECT+pic,pic_big,pic_small+FROM+event+WHERE+eid=%s&access_token=%s'

FB_GROUP_URL = r'http://www.facebook.com/groups/%s'
FB_GROUP_GRAPH = r'https://graph.facebook.com/%s/feed?access_token=%s'
FB_GROUP_MEMBERS_GRAPH = r'https://graph.facebook.com/%s/members/?limit=%s&offset=%s&access_token=%s'

FB_USER_GRAPH = r'https://graph.facebook.com/%s?fields=email,gender,devices&access_token=%s'


# http://php.net/manual/en/function.date.php
# http://developers.facebook.com/docs/reference/api/
# https://developers.facebook.com/apps
# http://developers.facebook.com/tools/explorer/
# http://developers.facebook.com/docs/authentication/
#FB_APP_ID = r''
#FB_APP_SECRET = r''

# old
# FB_GET_ACCESS_TOKEN = 'https://www.facebook.com/dialog/oauth?client_id=%s&redirect_uri=%s&response_type=token'
FB_GET_ACCESS_TOKEN = 'https://graph.facebook.com/oauth/access_token?grant_type=client_credentials&client_id=%s&client_secret=%s'


# for app? not user?
# https://www.facebook.com/dialog/oauth?client_id=%s&redirect_uri=https://DOMAIN/tasks/update-facebook-token&response_type=token
# http://tungwaiyip.info/blog/2011/02/19/facebook_oauth_authentication_flow
# http://developers.facebook.com/blog/post/2011/05/13/how-to--handle-expired-access-tokens/
#FB_GET_ACCESS_TOKEN = 'https://graph.facebook.com/oauth/access_token?client_id=%s&client_secret=%s&redirect_uri=http://DOMAIN/&code=%s'


class FacebookEventError(Exception):
    pass


class InvalidFacebookEvent(FacebookEventError):
    pass


class FacebookEventConnection(FacebookEventError):
    pass


class FacebookGraphAPI(object):
    def __init__(self, uid, fb_app_id=None, fb_app_secret=None, access_token=''):
        self.uid = uid
        self.properties = {}
        if fb_app_id:
            self.fb_app_id = fb_app_id
        else:
            self.fb_app_id = os.environ.get('FACEBOOK_API_KEY', '')
        if fb_app_secret:
            self.fb_app_secret = fb_app_secret
        else:
            self.fb_app_secret = os.environ.get('FACEBOOK_SECRET', '')

        self.access_token = access_token

    def request(self, url, content_type, timeout=240): # default 3 min of timeout
        try:
            return request(url, content_type, timeout=timeout)
        except urllib2.HTTPError as e:
            raise FacebookEventConnection(e), None, sys.exc_info()[2]
        except IOError as e:
            raise FacebookEventConnection(e), None, sys.exc_info()[2]

    def update_access_token(self):
        access_token = self.request(FB_GET_ACCESS_TOKEN % (self.fb_app_id, self.fb_app_secret), 'text/plain', timeout=30)
        self.access_token = access_token.replace('access_token=', '')

    def parse(self):
        pass


class FacebookEventPage(FacebookGraphAPI):
    """
    Facebook JSON Example:
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

    def __init__(self, uid, fb_app_id=None, fb_app_secret=None, access_token=''):
        super(FacebookEventPage, self).__init__(uid, fb_app_id=fb_app_id, fb_app_secret=fb_app_secret, access_token=access_token)
        self.flyer = None
        self.flyer_default = None
        self.flyer_big = None
        self.flyer_small = None

    def parse(self):
        self.update_access_token()
        url = FB_EVENT_GRAPH % (self.uid, self.access_token)
        logging.info(url)
        facebook_json = self.request(url, 'application/json')
        #logging.info(facebook_json)
        try:
            self.properties = json.loads(facebook_json)
            if not isinstance(self.properties, dict):
                logging.error(u'Error: %s' % self.properties)
                raise InvalidFacebookEvent(u'Não foi possível carregar a balada'), None, sys.exc_info()[2]
        except Exception as e:
            logging.error(u'Error: %s' % repr(e))
            raise InvalidFacebookEvent(e, u'Página do evento inválida'), None, sys.exc_info()[2]

        url = FB_EVENT_PICTURE_GRAPH % (self.uid, self.access_token)
        self.flyer = self.request(url, 'image/jpeg');

        url = FB_EVENT_ALL_PICTURES_GRAPH % (self.uid, self.access_token)
        flyers_info = self.request(url, 'application/json')
        flyers_info = json.loads(flyers_info)
        try:
            self.flyer_default = self.request(flyers_info['data'][0]['pic'], 'image/jpeg')
        except (KeyError, IndexError):
            pass
        try:
            self.flyer_big = self.request(flyers_info['data'][0]['pic_big'], 'image/jpeg')
        except (KeyError, IndexError):
            pass
        try:
            self.flyer_small = self.request(flyers_info['data'][0]['pic_small'], 'image/jpeg')
        except (KeyError, IndexError):
            pass

    def get_event_name(self):
        return self.properties['name']

    def get_location(self):
        return self.properties['location'] if 'location' in self.properties else u'Não especificado'

    def get_timestamp(self, timezone=0):
        fb_date = datetime.strptime(self.properties['start_time'], '%d/%m/%Y-%H:%M')
        if timezone:
            return fb_date + timedelta(hours=TIMEZONE)
        else:
            return fb_date

    def get_date(self, timezone=0):
        return self.get_timestamp(timezone=timezone).date()

    def get_time(self, timezone=0):
        # http://developers.facebook.com/docs/reference/api/
        return self.get_timestamp(timezone=timezone).time()

    def get_flyer(self):
        return self.flyer

    def get_flyer_default(self):
        return self.flyer_default

    def get_flyer_big(self):
        return self.flyer_big

    def get_flyer_small(self):
        return self.flyer_small


class FacebookGroupPage(FacebookGraphAPI):
    """
    Facebook JSON Example:
    http://developers.facebook.com/docs/reference/api/group/
    """

    def parse(self):
        self.update_access_token()
        url = FB_GROUP_GRAPH % (self.uid, self.access_token)
        logging.info(url)
        facebook_json = self.request(url, 'application/json')
        #logging.debug(facebook_json)
        try:
            self.properties = json.loads(facebook_json)
        except Exception as e:
            logging.error(u'Error: %s' % repr(e))
            raise InvalidFacebookEvent(e, u'Página do evento inválida'), None, sys.exc_info()[2]

    def get_event_ids(self):
        event_ids = []
        feeds = self.properties['data']
        for feed in feeds:
            url_re_expression = '.+facebook.com/events/(?P<event_id>\d+).*'
            if 'message' in feed:
                try:
                    event_id = re.search(url_re_expression, feed['message']).group(1)
                    event_ids.append(int(event_id))
                except AttributeError:
                    pass # not a event link
            if 'link' in feed:
                try:
                    event_id = re.search(url_re_expression, feed['link']).group(1)
                    event_ids.append(int(event_id))
                except AttributeError:
                    pass # not a event link
        return list(set(event_ids)) # remove replicated links

    def get_users(self, limit=100, offset=0):
        """
        {
           "data": [
              {
                 "name": "Marcelo Malaguti",
                 "id": "100002104458008",
                 "administrator": false
              },
              {...} ...
        }
        """
        # http://developers.facebook.com/tools/explorer/?method=GET&path=195466193802264%2Fmembers
        self.update_access_token()

        url = FB_GROUP_MEMBERS_GRAPH % (self.uid, limit, offset, self.access_token)
        logging.info(url)

        try:
            facebook_json = self.request(url, 'application/json')
            #logging.debug(facebook_json)
            return json.loads(facebook_json)['data']
        except Exception as e:
            logging.error(u'Error: %s' % repr(e))
            # raise FacebookGroupMembersError(e, u'Error to read members of group'), None, sys.exc_info()[2]
        return []


# https://developers.facebook.com/docs/reference/api/user/
class FacebookUserInfo(FacebookGraphAPI):
    def get_info(self):
        url = FB_USER_GRAPH % (self.uid, self.access_token)
        logging.info(url)
        try:
            facebook_json = self.request(url, 'application/json')
            #logging.debug(facebook_json)
            return json.loads(facebook_json)
        except Exception as e:
            logging.error(u'Error: %s' % repr(e))
        return {}

