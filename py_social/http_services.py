# coding: utf-8
import base64
import logging
import sys
import urllib2


def request(url, content_type, timeout=240, username=None, password=None, host=None):
    opener = urllib2.build_opener(urllib2.HTTPHandler)
    request = urllib2.Request(url)
    if host:
        request.add_header('Host', host)
    request.add_header('Accept', '*/*')
    request.add_header('Content-type', content_type)
    if username:
        base64string = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
        request.add_header("Authorization", "Basic %s" % base64string)
    #logging.info('HTTP Headers: %s' % request.headers)
    try:
        handler = opener.open(request, timeout=timeout)
        return handler.read()
    except urllib2.HTTPError as e:
        logging.error('HttpError %s: %s [%s]' % (e.code, repr(e), url))
        raise e, None, sys.exc_info()[2]
    except IOError as e:
        logging.error('IOError: %s' % repr(e))
        raise e, None, sys.exc_info()[2]
