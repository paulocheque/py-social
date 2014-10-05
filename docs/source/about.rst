.. about:

About
*******************************************************************************


Change Log
===============================================================================

Date format: yyyy/mm/dd

Version 0.1.9 (2014/03/31)
-------------------------------------------------------------------------------

* <http://pypi.python.org/pypi/py-social/0.1.9>
* [bugfix] Fixed Event flyer_urls method

Version 0.1.8 (2014/03/29)
-------------------------------------------------------------------------------

* [new] Event flyer_urls method
* [bugfix] Picture url bugged


Version 0.1.7 (2014/03/06)
-------------------------------------------------------------------------------

* [update] More logs in error scenario to tweet
* [bugfix] Bugfix in error scenarios

Version 0.1.6 (2014/03/06)
-------------------------------------------------------------------------------

* [bugfix] Deal with FB graph bug for latitude and longitude

Version 0.1.5 (2014/03/03)
-------------------------------------------------------------------------------

* [new] may return None on get fb_id from urls

Version 0.1.4 (2014/03/03)
-------------------------------------------------------------------------------

* [new] get_user_id_from_facebook_url method

Version 0.1.3 (2014/03/03)
-------------------------------------------------------------------------------

* [new] Event get_owner
* [new] set_log_level debug method

Version 0.1.2 (2014/03/02)
-------------------------------------------------------------------------------

* [new] Group/Event/Page pages option in load_feed method: load_feed(pages=1).
* [update] Using python logging system instead of print commands.

Version 0.1.1 (2014/03/02)
-------------------------------------------------------------------------------

* [new] Group/Event/Page has the option to load all feed

Version 0.1.0 (2014/02/20)
-------------------------------------------------------------------------------

* [new] Facebook spider
* [new] get Event/Page/Group users from feed.
* [new] get Event/Page/Group events from feed.
* [new] get Event users from maybe and attending.
* [new] get Group users from members.
* [update] FacebookEventPage renamed to FacebookEvent.
* [update] FacebookGroupPage renamed to FacebookGroup.
* [update] FacebookUserInfo renamed to FacebookUser.
* [update] FacebookEvent.get_event_name() renamed to FacebookEvent.get_name().

Version 0.0.1 (2014/02/01)
-------------------------------------------------------------------------------

* [new] FacebookEventPage.
* [new] FacebookGroupPage.
* [new] FacebookUserInfo.
* [new] tweet.






Collaborators
===============================================================================

Paulo Cheque <http://twitter.com/paulocheque> <https://github.com/paulocheque>


Pull Requests tips
===============================================================================

About commit messages
-------------------------------------------------------------------------------

* Messages in english only
* All messages have to follow the pattern: "[TAG] message"
* TAG have to be one of the following: new, update, bugfix, delete, refactoring, config, log, doc, mergefix

About the code
-------------------------------------------------------------------------------

* One change (new feature, update, refactoring, bugfix etc) by commit
* All bugfix must have a test simulating the bug
* All commit must have 100% of test coverage

Running tests
-------------------------------------------------------------------------------

Command::

    python manage.py test --with-coverage --cover-inclusive --cover-html --cover-package=your_package.*

TODO list
===============================================================================

Tests and Bugfixes
-------------------------------------------------------------------------------

*

Features
-------------------------------------------------------------------------------

*

Documentation
-------------------------------------------------------------------------------

*
