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
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from base.sitemap import sitemaps
from music.views import spotify_callback

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
    path('api-auth/', include('rest_framework.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('select2/', include('django_select2.urls')),
    path('sitemap.xml', sitemap, sitemaps, name='django.contrib.sitemaps.views.sitemap'),
    path(
        'robots.txt',
        lambda x: HttpResponse(
            "User-Agent: *\nDisallow: /admin/\n\nSitemap: https://www.benbb96.com/sitemap.xml",
            content_type="text/plain"
        ),
        name="robots_file"
    ),
    path('spotify_callback/', spotify_callback, name='spotify_callback')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += i18n_patterns(
    path('', include('base.urls')),
    path(_('review/'), include('avis.urls')),
    path(_('tracker/'), include('tracker.urls')),
    path(_('versus/'), include('versus.urls')),
    path(_('music/'), include('music.urls')),
    path(_('my-spot/'), include('my_spot.urls')),
    path(_('super-moite-moite/'), include('super_moite_moite.urls')),
    path(_('kendama/'), include('kendama.urls')),
    path(_('admin/'), admin.site.urls),
    # Auth Views
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('password-reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(),
        name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_complete'),
)

VIEW_NAMES = []  # Maintain a global list


def get_all_view_names(url_patterns, app_name=None):
    global VIEW_NAMES
    for pattern in url_patterns:
        if isinstance(pattern, URLResolver):
            get_all_view_names(pattern.url_patterns, pattern.namespace)  # call this function recursively
        elif isinstance(pattern, URLPattern):
            view_name = pattern.name  # get the view name
            if app_name and view_name:
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
