Motivators
==========

This is a Django application to generare [motivational posters][1] by
uploading images or providing an URL to an online image.

[1]: https://en.wikipedia.org/wiki/Motivational_poster "Wikipedia entry for motivational posters"

Requirements
------------

 - Python 2.6
 - Django 1.2.5 (later version may work)
 - Python Imaging Library 1.1.7 (if you install it with PIP, you must
   ensure you get JPEG, PNG and FREETYPE support)
 - A TTF font (Times works best) in data/font.ttf
 - jQuery 1.5 or later is required (1.5.2 in included in static/).

There is a flag additional to DEBUG in settings.py: DEV. It's used
to serve static content using Django dev server.

Configuration
-------------

Create a local.py file with your local configuration including (at least):

 - SECRET\_KEY
 - ADMINS
 - DEBUG (set to False for production)
 - SITE\_BASE
 - MEDIA\_URL

Author
------

 - Juan J. Martinez <jjm@usebox.net>

License
-------

This is free software under MIT license. Please check COPYING file for more
details.

