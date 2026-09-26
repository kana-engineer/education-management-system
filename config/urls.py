from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import path, include
from django.http import HttpResponse

from main.sitemaps import StaticViewSitemap, NewsSitemap


sitemaps = {
    "static": StaticViewSitemap,
    "news": NewsSitemap,
}


urlpatterns = [
    path("django-admin/", admin.site.urls),

    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),

    path(
    "robots.txt",
    lambda request: HttpResponse(
        "User-agent: *\n"
        "Allow: /\n"
        "Disallow: /admin/\n"
        "Disallow: /django-admin/\n"
        "Disallow: /login/\n"
        "Disallow: /sign-up/\n"
        "Sitemap: https://k-land.center/sitemap.xml\n",
        content_type="text/plain",
    ),
    ),

    path("", include("main.urls")),
]


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
