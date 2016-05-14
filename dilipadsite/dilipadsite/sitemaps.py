from django.contrib.sitemaps import Sitemap
from dilipadsite.models import datenav, basehansard
from django.contrib.sitemaps import GenericSitemap
from andablog.models import Entry

class ArticleSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        return Entry.objects.filter(is_draft=False)

    def lastmod(self, obj):
        return obj.pub_date

class SpeechSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.6
    
    def items(self):
        return basehansard.objects.all()

    def location(self, obj):
        return obj.get_permalink_url()

class DateSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.8
    
    def items(self):
        return datenav.objects.all()

    def location(self, obj):
        return obj.get_fullurl()

class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = 'weekly'

    def items(self):
        return ['data', 'help', 'home']

    def location(self, item):
        return reverse(item)

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
