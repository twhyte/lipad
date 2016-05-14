"""dilipadsite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
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
from django.contrib import admin
from search import urls as search_urls
from full import urls as full_urls
from help import urls as help_urls
from data import urls as data_urls
from members import urls as members_urls
from django.contrib.sitemaps.views import sitemap
from dilipadsite.sitemaps import *

sitemaps = {'articles' : ArticleSitemap,
            'speeches' : SpeechSitemap,
            'dates' : DateSitemap,
            'staticview' : StaticViewSitemap}

urlpatterns = [
    url(r'^grappelli/', include('grappelli.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^search/', include(search_urls, namespace="dilipadsearch")),
    url(r'^full/', include(full_urls)),
    url(r'^help/', include(help_urls), name = "help"),
    url(r'^members/', include(members_urls), name = "members"),
    url(r'^$', 'home.views.index', name = "home"),
    url(r'^blog/', include('andablog.urls', namespace='andablog')),
    url(r'^markitup/', include('markitup.urls')),
    url(r'^data/', include(data_urls), name = "data"),
    url(r'^contact/', include('django_contactme.urls')),
    url(r'^sitemap\.xml$', sitemap, {'sitemaps': sitemaps},
        name='django.contrib.sitemaps.views.sitemap')
]
