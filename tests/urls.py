from __future__ import unicode_literals

from django.conf.urls import patterns
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic import TemplateView


urlpatterns = patterns(
    '',
    (r'^/', TemplateView.as_view(template_name='base.html')),
)

urlpatterns += staticfiles_urlpatterns()
