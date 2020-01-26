from django.conf.urls import include
from django.conf.urls.i18n import i18n_patterns
from django.conf import settings
from django.contrib import admin
from django.conf.urls.static import static
from django.http import HttpResponse
from django.urls import path, URLResolver, URLPattern
from django.contrib.auth import views as auth_views
from django.contrib.sitemaps.views import sitemap
from django.utils.translation import gettext_lazy as _

from base.sitemap import sitemaps


urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
    path('api-auth/', include('rest_framework.urls')),
    path('sitemap.xml', sitemap, sitemaps, name='django.contrib.sitemaps.views.sitemap'),
    path(
        'robots.txt',
        lambda x: HttpResponse(
            "User-Agent: *\nDisallow: /admin/\n\nSitemap: http://benbb96.pythonanywhere.com/sitemap.xml",
            content_type="text/plain"
        ),
        name="robots_file"
    )
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += i18n_patterns(
    path('', include('base.urls')),
    path(_('review/'), include('avis.urls')),
    path(_('tracker/'), include('tracker.urls')),
    path(_('versus/'), include('versus.urls')),
    path(_('music/'), include('music.urls')),
    path(_('my-spot/'), include('my_spot.urls')),
    path(_('admin/'), admin.site.urls),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout')
)

VIEW_NAMES = []  # Maintain a global list


def get_all_view_names(url_patterns, app_name=None):
    global VIEW_NAMES
    for pattern in url_patterns:
        if isinstance(pattern, URLResolver):
            get_all_view_names(pattern.url_patterns, pattern.namespace)  # call this function recursively
        elif isinstance(pattern, URLPattern):
            view_name = pattern.name  # get the view name
            if app_name:
                view_name = app_name + ':' + view_name
            VIEW_NAMES.append(view_name)  # add the view to the global list
    return VIEW_NAMES


# Load VIEW NAMES
get_all_view_names(urlpatterns)


if 'debug_toolbar' in settings.INSTALLED_APPS:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
