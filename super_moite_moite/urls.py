from django.urls import path

from . import views

app_name = 'super-moite-moite'

urlpatterns = [
    path('', views.liste_logements, name='liste-logements'),
    path('logement/<slug>', views.LogementDetailView.as_view(), name='detail-logement'),
]
