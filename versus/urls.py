from django.contrib.auth.decorators import login_required
from django.urls import path

from . import views

app_name = 'versus'

urlpatterns = [
    path('', views.JeuListView.as_view(), name='liste-jeux'),
    path('<slug:slug>', views.JeuDetailView.as_view(), name='detail-jeu')
]
