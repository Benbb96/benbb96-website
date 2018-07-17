from django.conf.urls import include
from django.contrib import admin
from django.conf.urls.static import static
from django.urls import path
from django.views.generic import TemplateView

from benbb96 import settings

urlpatterns = [
    path('', include('base.urls')),
    path('avis/', include('avis.urls')),
    path('admin/', admin.site.urls)
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
