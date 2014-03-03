PySocial
====================

![Continuous Integration Status](https://secure.travis-ci.org/paulocheque/PySocial.png)

#### Latest version: 0.1.0 (2013/../..)

DESCRIPTOIN

* [Basic Example of Usage](#basic-example-of-usage)
  * [Submenu](#submenu)
* [Installation](#installation)
* [Change Log](#change-log)
* [TODO](#todo)

Basic Example of Usage
------------------------

```python
# Example of Usage
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
print fb.get_email()
print fb.get_field('username')

fb = FacebookPage(page_id, app_id=TEST_FB_APP_ID, app_secret=TEST_FB_APP_SECRET)
fb.load()
fb.load_feed()
print len(fb.get_all_users_ids())
print len(fb.get_events_ids_from_feed())

fb = FacebookEvent(event_id, app_id=TEST_FB_APP_ID, app_secret=TEST_FB_APP_SECRET)
fb.load()
fb.load_feed()
fb.load_maybe()
fb.load_attending()
fb.load_small_flyer()
fb.load_flyers()
print len(fb.get_all_users_ids())
print len(fb.get_events_ids_from_feed())

fb = FacebookGroup(group_id, app_id=TEST_FB_APP_ID, app_secret=TEST_FB_APP_SECRET)
fb.load()
fb.load_feed()
fb.load_members()
print len(fb.get_all_users_ids())
print len(fb.get_events_ids_from_feed())

# To load all feed:
while fb.has_feed_to_load():
  fb.load_feed()

# or
fb.load_feed(pages=10)
```

Submenu
------------
```python
```


Installation
------------

```
pip install PySocial
```

#### or

```
1. Download zip file
2. Extract it
3. Execute in the extracted directory: python setup.py install
```

#### Development version

```
pip install -e git+git@github.com:paulocheque/PySocial.git#egg=PySocial
```

#### requirements.txt

```
PySocial==VERSION
# or use the development version
git+git://github.com/paulocheque/PySocial.git#egg=PySocial
```

#### Upgrade:

```
pip install PySocial --upgrade --no-deps
```

#### Requirements

* Python 2.7 / 3.3
* Tested with 2.7


Change Log
-------------

#### 0.1.4 (2014/03/03)

* [new] get_user_id_from_facebook_url method

#### 0.1.3 (2014/03/03)

* [new] Event get_owner
* [new] set_log_level debug method

#### 0.1.2 (2014/03/02)

* [new] Group/Event/Page pages option in load_feed method: load_feed(pages=1).
* [update] Using python logging system instead of print commands.

#### 0.1.1 (2014/03/02)

* [new] Group/Event/Page has the option to load all feed

#### 0.1.0 (2014/02/20)

* [new] Facebook spider
* [new] get Event/Page/Group users from feed.
* [new] get Event/Page/Group events from feed.
* [new] get Event users from maybe and attending.
* [new] get Group users from members.
* [update] FacebookEventPage renamed to FacebookEvent.
* [update] FacebookGroupPage renamed to FacebookGroup.
* [update] FacebookUserInfo renamed to FacebookUser.
* [update] FacebookEvent.get_event_name() renamed to FacebookEvent.get_name().

#### 0.0.1 (2014/02/01)

* [new] FacebookEventPage.
* [new] FacebookGroupPage.
* [new] FacebookUserInfo.
* [new] tweet.


TODO
-------------

* ...
