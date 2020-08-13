from django.urls import path

from . import views

app_name = 'versus'

urlpatterns = [
    path('jeux/', views.JeuListView.as_view(), name='liste-jeux'),
    path('jeux/<slug:slug>', views.JeuDetailView.as_view(), name='detail-jeu'),
    path('jeux/<slug:slug>/ajout', views.ajout_partie, name='ajout-partie'),
    path(
        'jeux/<slug:slug>/edition/<int:partie_id>',
        views.edition_partie,
        name='edition-partie'
    ),
    path(
        'jeux/<slug:slug>/suppression/<int:partie_id>',
        views.suppression_partie,
        name='suppression-partie'
    ),
    path('joueurs/', views.JoueurListView.as_view(), name='liste-joueurs'),
    path(
        'joueurs/<slug:slug>',
        views.JoueurDetailView.as_view(),
        name='detail-joueur'
    ),
]
