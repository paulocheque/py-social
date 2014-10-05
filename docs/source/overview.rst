.. _more:

Getting Started
*******************************************************************************

Example of Usage
===============================================================================

Example::

    import os
    from py_social.facebook_services import *

    TEST_FB_APP_ID = os.getenv('FACEBOOK_API_KEY', '?')
    TEST_FB_APP_SECRET = os.getenv('FACEBOOK_API_SECRET', '?')
    user_id = '?'
    page_id = '?'
    event_id = '?'
    group_id = '?'

    fb = FacebookUser(user_id, app_id=TEST_FB_APP_ID, app_secret=TEST_FB_APP_SECRET)
    fb.load(fields='email,username')
    print(fb.get_email())
    print(fb.get_field('username'))

    fb = FacebookPage(page_id, app_id=TEST_FB_APP_ID, app_secret=TEST_FB_APP_SECRET)
    fb.load()
    fb.load_feed()
    print(len(fb.get_all_users_ids()))
    print(len(fb.get_events_ids_from_feed()))

    fb = FacebookEvent(event_id, app_id=TEST_FB_APP_ID, app_secret=TEST_FB_APP_SECRET)
    fb.load()
    fb.load_feed()
    fb.load_maybe()
    fb.load_attending()
    fb.load_small_flyer()
    fb.load_flyers()
    print(len(fb.get_all_users_ids()))
    print(len(fb.get_events_ids_from_feed()))

    fb = FacebookGroup(group_id, app_id=TEST_FB_APP_ID, app_secret=TEST_FB_APP_SECRET)
    fb.load()
    fb.load_feed()
    fb.load_members()
    print(len(fb.get_all_users_ids()))
    print(len(fb.get_events_ids_from_feed()))

    # To load all feed:
    while fb.has_feed_to_load():
      fb.load_feed()

    # or
    fb.load_feed(pages=10)


Section 2
===============================================================================

SubSection 2.1
-------------------------------------------------------------------------------

In file.py::

    Settings = False

