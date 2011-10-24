from django.conf.urls.defaults import include, patterns, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

import gobotany.api.urls
import gobotany.core.urls

handler404 = 'django.views.defaults.page_not_found'
handler500 = 'django.views.defaults.server_error'

admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include('gobotany.api.urls')),
    url(r'^core/', include('gobotany.core.urls')),
    url(r'^tinymce/', include('tinymce.urls')),
    url(r'^', include('gobotany.simplekey.urls')),
    )

if gobotany.settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()

if gobotany.settings.DEBUG_DOJO:
    import os
    import gobotany
    dojo_path = os.path.abspath(os.path.join(gobotany.__path__[0],
                                             '..', '..', '..', 'dojo'))
    urlpatterns += patterns(
        '',
        (r'^dojo/(?P<path>.*)$', 'django.views.static.serve',
         {'document_root': dojo_path,
          'show_indexes': True}),
        )
