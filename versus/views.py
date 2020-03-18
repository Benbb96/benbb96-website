from django.shortcuts import render
from django.views.generic import ListView, DetailView

from versus.models import Jeu, Joueur


class JeuListView(ListView):
    model = Jeu


class JeuDetailView(DetailView):
    model = Jeu
    slug_field = 'slug'
    queryset = Jeu.objects.select_related('createur__user').prefetch_related('parties__partiejoueur_set__joueur')


class JoueurDetailView(DetailView):
    model = Joueur
    slug_field = 'slug'
    queryset = Joueur.objects.select_related('profil__user').prefetch_related(
        'partie_set__jeu', 'partie_set__partiejoueur_set__joueur',
        'partiejoueur_set__partie__jeu', 'partiejoueur_set__partie__partiejoueur_set',
    )
