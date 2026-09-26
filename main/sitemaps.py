from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import News


class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = "weekly"

    def items(self):
        return [
            "main:home",
            "main:about",
            "main:courses",
            "main:apply_course",
            "main:contackt",
            "main:news",
            "main:corey",
            "main:admission_korea",
        ]

    def location(self, item):
        return reverse(item)


class NewsSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return News.objects.filter(is_published=True)

    def location(self, obj):
        return reverse("main:news_detail", args=[obj.id])

    def lastmod(self, obj):
        return obj.created_at
