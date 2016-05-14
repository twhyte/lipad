"""The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
import views
from django.views.generic import RedirectView

urlpatterns = [

    url(r'^$', views.index, name='index'),
    url(r'^(?P<year>[0-9]{4})/$', views.year_view),
    url(r'^(?P<year>[0-9]{4})/(?P<month>[0-9]{2})/$', views.month_view),
    url(r'^(?P<year>[0-9]{4})/(?P<month>[0-9]{2})/(?P<day>[0-9]{2})/$', views.hansard_day_redirect),
    url(r'^(?P<year>[0-9]{4})/(?P<month>[0-9]{2})/(?P<day>[0-9]{2})/(?P<pageno>[0-9]+)/$', views.hansard_view, name="hansardview"),
    url(r'^(?P<year>[0-9]{4})/(?P<month>[0-9]{2})/(?P<day>[0-9]{2})/fullview/(?P<pk>[0-9]+)/$', views.hansard_full_view_redirect),
    url(r'^(?P<year>[0-9]{4})/(?P<month>[0-9]{2})/(?P<day>[0-9]{2})/exportcsv/$', views.full_csv_export_view),
    url(r'^permalink/(?P<pk>[0-9]+)/', views.permalink_view),

]
