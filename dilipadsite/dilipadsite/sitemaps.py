from django.contrib.sitemaps import Sitemap
from dilipadsite.models import datenav, basehansard, member
from django.contrib.sitemaps import GenericSitemap
from andablog.models import Entry
from django.core.urlresolvers import reverse
import datetime

class AbstractSitemapClass():
    changefreq = 'daily'
    url = None
    def get_absolute_url(self):
        return self.url

class ArticleSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        return Entry.objects.all()

    def lastmod(self, obj):
        return obj.published_timestamp

class MemberSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        return member.objects.all()

    def location(self, obj):
        return ("/members/record/"+obj.pid+"/")

class DateSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.8
    
    def items(self):
        return datenav.objects.all()

    def location(self, obj):
        return obj.get_fullurl(obj.get_year(),obj.get_month(),obj.day)

class StaticViewSitemap(Sitemap):  
    pages = {
             'home':'/', #Add more static pages here like this 'example':'url_of_example',
             'data':'/data/',
             'help':'/help/',
             }
    main_sitemaps = []
    for page in pages.keys():
        sitemap_class = AbstractSitemapClass()
        sitemap_class.url = pages[page]        
        main_sitemaps.append(sitemap_class)

    def items(self):
        return self.main_sitemaps    
    lastmod = datetime.datetime(2016, 7, 22)   #Enter the year,month, date you want in yout static page sitemap.
    priority = 1
    changefreq = "monthly"   

class EntrySitemap(Sitemap):
    """
    Sitemap for entries.
    """
    priority = 0.5
    changefreq = 'weekly'

    def items(self):
        """
        Return published entries.
        """
        return Entry.objects.filter(is_published=True).order_by('-published_timestamp')

    def lastmod(self, obj):
        """
        Return last modification of an entry.
        """
        return obj.modified
