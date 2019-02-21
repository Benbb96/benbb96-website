from django.urls import path
from django.views.generic import TemplateView

from . import views

urlpatterns = [
    path('', views.ProjetListView.as_view(), name='home'),
    path('about', TemplateView.as_view(template_name='base/about.html'), name='about'),
    path('rallye-des-colocs', TemplateView.as_view(template_name='base/rallye.html'), name='rallye'),
    path('gallery', TemplateView.as_view(template_name='base/gallery.html'), name='gallery'),
    path('profil/<str:slug>', views.ProfilDetailView.as_view(), name='profil')
]
