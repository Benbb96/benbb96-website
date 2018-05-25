from django.conf.urls import include
from django.contrib import admin
from django.conf.urls.static import static
from django.urls import path
from django.views.generic import TemplateView

from benbb96 import settings

urlpatterns = [
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('gallery', TemplateView.as_view(template_name='gallery.html'), name='gallery'),
    path('avis/', include('avis.urls')),
    path('admin/', admin.site.urls)
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
