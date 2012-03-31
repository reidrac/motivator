"""
Motivators - public/urls.py
Copyright (C) 2011,2012 by Juan J. Martinez <jjm@usebox.net>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""
from django.conf.urls.defaults import *
from motivator.public.views import *

urlpatterns = patterns('',
    (r'^$', welcome_view),
    (r'^init-creator/$', init_creator_view),
    (r'^creator/(?P<session>[0-9a-z]+)/$', creator_view),
    (r'^creator-preview/(?P<session>[0-9a-z]+)/$', creator_preview),
    (r'^creator-done/(?P<session>[0-9a-z]+)/$', creator_done_view),
    (r'^m/(?P<slug>[-\w]+)\.html$', motivator_view),
    (r'^nsfw/(?P<slug>[-\w]+)\.html$', motivator_nsfw_view),
    (r'^rss/?$', feed_view),
)

handler404 = 'motivator.public.views.not_found_view'
handler500 = 'motivator.public.views.server_error_view'

