# coding: utf-8
# Selenium script to post message in Facebook
import logging
import os
import re

from selenium import webdriver


class FacebookSpider(object):
    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.driver = None

    def start(self):
        # https://code.google.com/p/selenium/wiki/PythonBindings
        # Depends on: java - jar selenium-server.jar
        # self.driver = webdriver.Remote(desired_capabilities=webdriver.DesiredCapabilities.HTMLUNITWITHJS)
        self.driver = webdriver.Chrome()
        self.driver.get('http://facebook.com')

    def authenticate(self):
        email = self.driver.find_element_by_id('email')
        email.send_keys(self.email)
        password = self.driver.find_element_by_id('pass')
        password.send_keys(self.password)
        login_button = self.driver.find_elements_by_xpath("//input[@type='submit' and @value='Log In']")[0]
        login_button.click()

    def send_message(self, facebook_id, message):
        try:
            print('Message to %s' % (facebook_id))
            self.driver.get('http://facebook.com/messages/%s' % facebook_id)

            if message in self.driver.page_source:
                print(u'This message has already been sent to the user: %s' % facebook_id)
                return False

            text_area = self.driver.find_elements_by_xpath("//textarea[@name='message_body']")[0]
            text_area.send_keys(message)

            try:
                send_button = self.driver.find_elements_by_xpath("//input[@type='submit' and @value='Send']")[0]
            except IndexError:
                send_button = self.driver.find_elements_by_xpath("//input[@type='submit' and @value='Reply']")[0]
            send_button.click()
            print('OK: %s' % facebook_id)
        except Exception as e:
            logging.exception(e)
            print(repr(e))
            print('FAIL: %s' % facebook_id)
            # print(self.driver.page_source)
            return False
        return True

    def send_messages(self, facebook_ids, message):
        succeeded_ids = []
        for facebook_id in facebook_ids:
            if self.send_message(facebook_id, message):
                succeeded_ids.append(facebook_id)
        return succeeded_ids

    def close(self):
        if self.driver:
            self.driver.quit()


def send_facebook_messages(facebook_ids, message, email=None, password=None):
    if facebook_ids:
        email = email if email else os.getenv('FB_EMAIL')
        password = password if password else os.getenv('FB_PASS')
        spider = FacebookSpider(email, password)
        try:
            spider.start()
            spider.authenticate()
            succeeded_ids = spider.send_messages(facebook_ids, message)
            return succeeded_ids
        finally:
            spider.close()
    else:
        print('No Facebook id to send message')
    return []


def colorize(message, color='blue'):
    color_codes = dict(black=30, red=31, green=32, yellow=33, blue=34, magenta=35, cyan=36, white=37)
    code = color_codes.get(color, 34)
    msg = '\033[%(code)sm%(message)s\033[0m' % {'code':code, 'message':message}
    # print(msg)
    return msg


# python scripts/send_facebook_message.py facebook_msg.txt facebook_ids.txt USER PASSWORD
if __name__ == '__main__':
    import os
    import sys
    import argparse
    import logging

    try:
        pass
    except ImportError as e:
        print(os.getcwd())
        print(sys.path)
        raise e

    BEER = '\xF0\x9f\x8d\xba '
    VERSION = 1
    print(colorize('%s - Facebook Spider (%s)' % (BEER, VERSION), color='yellow'))

    parser = argparse.ArgumentParser()
    parser.add_argument('msg', help='Filename with the message to be sent')
    parser.add_argument('fb_ids', help='Filename with Facebook ids separated by commas')
    parser.add_argument('fb_email', help='Facebook email')
    parser.add_argument('fb_pass', help='Facebook password')
    args = parser.parse_args()

    print(colorize('::: Sending message', color='blue'))

    f = open(args.msg, 'r')
    message = f.read().decode('utf-8')
    f.close()

    f = open(args.fb_ids, 'r')
    facebook_ids = f.read().decode('utf-8').strip().split(',')
    facebook_ids = filter(str, facebook_ids)
    f.close()

    email = args.fb_email
    password = args.fb_pass
    send_facebook_messages(facebook_ids, message, email, password)
