from django.conf.urls.defaults import *
from django.contrib import admin
admin.autodiscover()

import motivator.settings as settings

urlpatterns = patterns('',
    (r'', include('motivator.public.urls')),
    (r'^_admin/', include(admin.site.urls)),
)

if settings.DEV:
    urlpatterns += patterns('',
        (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': './static/'}),
        (r'^mediax/(?P<path>.*)$', 'django.views.static.serve', {'document_root': './media/'}),
    )

