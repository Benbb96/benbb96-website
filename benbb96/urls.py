from django.conf.urls import include
from django.contrib import admin
from django.conf.urls.static import static
from django.urls import path
from django.contrib.auth import views as auth_views

from benbb96 import settings

urlpatterns = [
    path('', include('base.urls')),
    path('avis/', include('avis.urls')),
    path('tracker/', include('tracker.urls')),
    path('music/', include('music.urls')),
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
