from django.conf.urls import include
from django.contrib import admin
from django.conf.urls.static import static
from django.contrib.sitemaps import GenericSitemap
from django.http import HttpResponse
from django.urls import path
from django.contrib.auth import views as auth_views
from django.contrib.sitemaps.views import sitemap

from avis.models import Avis, Produit, Structure
from benbb96 import settings
from benbb96.sitemaps import StaticViewSitemap

avis_dict = {
    'queryset': Avis.objects.all(),
    'date_field': 'date_creation',
}

produit_dict = {
    'queryset': Produit.objects.all(),
    'date_field': 'date_creation',
}

structure_dict = {
    'queryset': Structure.objects.all(),
    'date_field': 'date_creation',
}

urlpatterns = [
    path('', include('base.urls')),
    path('avis/', include('avis.urls')),
    path('tracker/', include('tracker.urls')),
    path('versus/', include('versus.urls')),
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path(
        'sitemap.xml',
        sitemap,
        {'sitemaps': {
            'static': StaticViewSitemap,
            'avis': GenericSitemap(avis_dict, priority=0.6),
            'produits': GenericSitemap(produit_dict, priority=0.4),
            'structures': GenericSitemap(structure_dict, priority=0.5)
        }},
        name='django.contrib.sitemaps.views.sitemap'
    ),
    path(
        'robots.txt',
        lambda x: HttpResponse(
            "User-Agent: *\nDisallow: /admin/\n\nSitemap: http://benbb96.pythonanywhere.com/sitemap.xml",
            content_type="text/plain"
        ),
        name="robots_file"
    )
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
