from django.shortcuts import render
from django.views.generic import ListView, DetailView

from versus.models import Jeu, Joueur


class JeuListView(ListView):
    model = Jeu


class JeuDetailView(DetailView):
    model = Jeu
    slug_field = 'slug'


class JoueurDetailView(DetailView):
    model = Joueur
    slug_field = 'slug'