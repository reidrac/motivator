"""
Motivators - public/models.py
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
from django.db import models
import motivator.settings as settings
import os

class Motivator(models.Model):
    """Storge motivational poster data."""
    slug = models.SlugField(max_length=255, unique=True)
    title = models.CharField(max_length=64, blank=True)
    text = models.CharField(max_length=128, blank=True)
    filename = models.CharField(max_length=128, unique=True)
    nsfw = models.BooleanField(default=False)
    editors_pick = models.BooleanField(default=False, help_text="display the motivator on the front page")
    creator_ip = models.IPAddressField()
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    @staticmethod
    def base_dir(filename):
        return "%s/%s" % (settings.MEDIA_ROOT, filename[:2])

    def delete(self, *args, **kwargs):
        base_dir = Motivator.base_dir(self.filename)
        os.unlink('%s/%s.png' % (base_dir, self.filename))
        os.unlink('%s/%s.jpg' % (base_dir, self.filename))
        os.unlink('%s/small_%s.jpg' % (base_dir, self.filename))
        os.unlink('%s/thumb_%s.jpg' % (base_dir, self.filename))

        super(Motivator, self).delete(*args, **kwargs)

    def url(self):
        return "/m/%s.html" % self.slug
    def full_url(self):
        return "%s%s" % (settings.SITE_BASE, self.url()[1:])
    def img(self):
        return "%s%s/small_%s.jpg" % (settings.MEDIA_URL, self.filename[:2], self.filename)
    def full_img(self):
        return "%s%s/%s.jpg" % (settings.MEDIA_URL, self.filename[:2], self.filename)
    def thumb_img(self):
        return "%s%s/thumb_%s.jpg" % (settings.MEDIA_URL, self.filename[:2], self.filename)

class BannedIp(models.Model):
    ip = models.IPAddressField()
    reason = models.CharField(max_length=255, help_text="eg. inadequate content")
    created = models.DateTimeField(auto_now_add=True)

