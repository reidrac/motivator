"""
Motivators - public/views.py
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
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django import forms
from django.contrib import messages
from django.template.defaultfilters import slugify
from motivator.public.models import Motivator, BannedIp
import motivator.settings as settings

from uuid import uuid4
import urllib2
import StringIO
import os
import random

from PIL import Image, ImageDraw, ImageFont, ImageFile
ImageFile.MAXBLOCK = 1024*1024

def welcome_view(request, template="index.html"):
    """
    Front page.

    Displays a random motivator based on the editor's pick flag.
    """
    if 'processed' in request.session:
        request.session.clear()

    try:
        motivator = Motivator.objects.filter(nsfw=False, editors_pick=True)
    except Motivator.DoesNotExist:
        motivator = None
    else:
        if motivator.count() > 1:
            motivator = random.choice(motivator)
        else:
            motivator = motivator[0]

    return render_to_response(template, dict(settings=settings, motivator=motivator), context_instance=RequestContext(request))

class GetImageForm(forms.Form):
    """User input, can be either an file or an URL."""
    file  = forms.FileField(required=False)
    # FIXME: validator for the URL (allow only JPEG or PNG files)
    url = forms.CharField(max_length=255, required=False)

def init_creator_view(request):
    """Initialise the creator view."""
    if request.POST:
        form = GetImageForm(request.POST, request.FILES)
        if form.is_valid():
            # file upload takes preference over the URL provided image
            if 'file' in request.FILES:
                # FIXME: not efficient for big files
                base_image = StringIO.StringIO()
                for chunk in request.FILES['file'].chunks():
                    base_image.write(chunk)

                session = "f%s" % uuid4().hex
                request.session['base_image'] = base_image.getvalue()
                base_image.close()
                request.session['session'] = session
                return HttpResponseRedirect(reverse(creator_view, args=[session]))
            elif form.cleaned_data['url']:
                base_image = StringIO.StringIO()
                try:
                    fd = urllib2.urlopen(form.cleaned_data['url'])
                    base_image.write(fd.read())
                except:
                    messages.error(request, "Failed to download the base image. Please check the URL and try again.")
                else:
                    session = "u%s" % uuid4().hex
                    request.session['base_image'] = base_image.getvalue()
                    base_image.close()
                    request.session['session'] = session
                    return HttpResponseRedirect(reverse(creator_view, args=[session]))

    return HttpResponseRedirect(reverse(welcome_view))

class CreatorForm(forms.Form):
    """Motivator user data."""
    title = forms.CharField(max_length=32, required=False)
    text = forms.CharField(max_length=80, required=False, widget=forms.TextInput(attrs=dict(size=40)))

def creator_view(request, session, template="create.html"):
    """Motivator creator view."""
    if not request.session.get('base_image', None) or not request.session.get('session', None):
        request.session.clear()
        messages.error(request, "No base image data found.")
        return HttpResponseRedirect(reverse(welcome_view))

    if request.session['session'] != session:
        request.session.clear()
        messages.error(request, "Invalid session. Please provide a base image to start creating your motivator!")
        return HttpResponseRedirect(reverse(welcome_view))

    # check bans -- TODO: proxies?
    creator_ip = request.META.get('REMOTE_ADDR', None)
    if BannedIp.objects.filter(ip=creator_ip).count() != 0:
        request.session.clear()
        messages.error(request, "We hate when this happens, but we can't accept your request!")
        return HttpResponseRedirect(reverse(welcome_view))

    form = CreatorForm(request.POST)

    if form.is_valid():
        title = form.cleaned_data['title'].upper().strip()
        text = form.cleaned_data['text'].capitalize().strip()
    else:
        title = ''
        text = ''

    # pre-process the base image once
    if not 'processed' in request.session:
        try:
            in_img = StringIO.StringIO(request.session['base_image'])
            img = Image.open(in_img)
            if img.format not in ('JPEG', 'PNG'):
                raise IOError('Not a JPEG or PNG file')

            # put the base image
            w, h = img.size
            if w > 720 or w < 300:
                h = 720*h/w
                w = 720

            base = Image.new('RGB', (w+80, h+240))
            base.paste(img.resize((w, h), Image.ANTIALIAS), (40, 40))

            # draw the frame
            draw = ImageDraw.Draw(base)
            draw.rectangle([36, 36, w+43, h+43], outline='#fae013')

            out = StringIO.StringIO()
            base.save(out, 'PNG')
            request.session['base_image'] = out.getvalue()
            out.close()
        except:
            request.session.clear()
            messages.error(request, "Failed to process base image data. Please check the file is a valid JPG or PNG image.")
            return HttpResponseRedirect(reverse(welcome_view))

    try:
        if 'base' in locals():
            img = base
        else:
            in_img = StringIO.StringIO(request.session['base_image'])
            img = Image.open(in_img)

        # our reference is the original image size
        w, h = img.size
        w -= 80
        h -= 240

        draw = ImageDraw.Draw(img)

        # draw the title
        if title:
            title_size = 100
            font = ImageFont.truetype("data/font.ttf", title_size)
            tw, th = font.getsize(title)
            while tw > w:
                title_size -= 5
                font = ImageFont.truetype("data/font.ttf", title_size)
                tw, th = font.getsize(title)

            draw.text(((w+80-tw)/2, h+60), title, font=font, fill='#fae013')

            # draw the text
            if text:
                text_size = int(title_size/1.8)
                text_size = text_size if text_size < 35 else 35
                font = ImageFont.truetype("data/font.ttf", text_size)
                ttw, tth = font.getsize(text)

                # FIXME: this code is ugly
                while ttw > w+70:
                    text_size -= 5
                    font = ImageFont.truetype("data/font.ttf", text_size)
                    ttw, tth = font.getsize(text)

                draw.text(((w+80-ttw)/2, h+th+60), text, font=font, fill='#f0f0f0')

        out = StringIO.StringIO()
        img.save(out, 'PNG')
        request.session['processed'] = out.getvalue()
        out.close()
    except:
        request.session.clear()
        messages.error(request, "Failed to process the image because of an unexpected problem. Sorry about that.")
        return HttpResponseRedirect(reverse(welcome_view))

    # the user is "done" with the motivator
    if 'done' in request.POST:
        request.session['title'] = title
        request.session['text'] = text
        return HttpResponseRedirect(reverse(creator_done_view, args=[session]))

    return render_to_response(template, locals(), context_instance=RequestContext(request))

def creator_preview(request, session):
    """Motivator preview, returns a PNG image."""
    if not request.session.get('processed', None) or not request.session.get('session', None):
        raise Http404()

    if request.session['session'] != session:
        raise Http404()

    response = HttpResponse(mimetype="image/png")
    response.content = request.session['processed']
    response['Cache-Control'] = 'no-cache'
    response['X-Preview'] = 'True'
    return response

def creator_done_view(request, session):
    """Exit view for the creator, save the generated motivator."""
    if not request.session.get('processed', None) or not request.session.get('session', None):
        request.session.clear()
        messages.error(request, "No base image data found.")
        return HttpResponseRedirect(reverse(welcome_view))

    if request.session['session'] != session:
        request.session.clear()
        messages.error(request, "Invalid session. Please provide a base image to start creating your motivator!")
        return HttpResponseRedirect(reverse(welcome_view))

    title = request.session.get('title', None)
    text = request.session.get('text', None)
    filename = uuid4().hex
    # FIXME: non ascii characters
    slug = slugify("%s-%s-%s" % (title, text, filename[:4]))
    # TODO: proxies
    creator_ip = request.META.get('REMOTE_ADDR', None)
    base_dir = Motivator.base_dir(filename[:2])

    # create the directory if it doesn't exist yet
    if not os.path.exists(base_dir):
        # beware directory permissions!
        os.makedirs(base_dir)

    # use PNG for high quality
    with open('%s/%s.png' % (base_dir, filename), 'w') as fd:
        fd.write(request.session['processed'])

    # FIXME: this should be a transaction, cleaning up if something fails
    in_img = StringIO.StringIO(request.session['processed'])
    img = Image.open(in_img)
    w, h = img.size
    with open('%s/small_%s.jpg' % (base_dir, filename), 'w') as fd:
        img.copy().resize((480, 480*h/w), Image.ANTIALIAS).save(fd, 'JPEG', optimize=True)
    with open('%s/thumb_%s.jpg' % (base_dir, filename), 'w') as fd:
        img.copy().resize((120, 120*h/w), Image.ANTIALIAS).save(fd, 'JPEG', optimize=True)
    with open('%s/%s.jpg' % (base_dir, filename), 'w') as fd:
        img.save(fd, 'JPEG')

    motivator = Motivator(slug = slug, title = title, text = text, filename = filename, creator_ip = creator_ip)
    motivator.save()

    return HttpResponseRedirect(reverse(motivator_view, args=[slug]))

def motivator_view(request, slug, template="motivator.html"):
    """Motivator main view."""
    try:
        motivator = Motivator.objects.get(slug=slug)
    except Motivator.DoesNotExist:
        raise Http404()

    # redirect to the warning view if it is a NSFW motivator
    # TODO: use something smarter than a GET parameter that can be too
    # easy to forge (a cookie?)
    if motivator.nsfw and not request.GET.get('ok-nsfw', None):
        return HttpResponseRedirect(reverse(motivator_nsfw_view, args=[slug]))

    # navigation (prev)
    mprevious = Motivator.objects.filter(created__lt=motivator.created, nsfw=False).order_by('-created')
    if mprevious.count():
        mprevious = mprevious[0]
    else:
        mprevious = None

    # navigation (next)
    mnext = Motivator.objects.filter(created__gt=motivator.created, nsfw=False).order_by('created')
    if mnext.count():
        mnext = mnext[0]
    else:
        mnext = None

    return render_to_response(template, locals(), context_instance=RequestContext(request))

def motivator_nsfw_view(request, slug, template="nsfw.html"):
    """Show a NSFW warning before continuing to the motivator."""
    try:
        motivator = Motivator.objects.get(slug=slug)
    except Motivator.DoesNotExist:
        raise Http404()

    if not motivator.nsfw:
        return HttpResponseRedirect(reverse(motivator_view, args=[slug]))

    return render_to_response(template, locals(), context_instance=RequestContext(request))

def feed_view(request, template="rss.html"):
    """RSS view."""
    try:
        motivators = Motivator.objects.filter(nsfw=False).order_by('-created')[:10]
    except Motivator.DoesNotExist:
        motivators = None

    pub_date = motivators[0].created
    base_url = settings.SITE_BASE
    return render_to_response(template, locals(), context_instance=RequestContext(request))

def not_found_view(request, template="404.html"):
    return render_to_response(template, locals(), context_instance=RequestContext(request))

def server_error_view(request, template="500.html"):
    return render_to_response(template, locals(), context_instance=RequestContext(request))

