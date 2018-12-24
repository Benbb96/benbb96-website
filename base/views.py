from django.contrib.auth.models import User
from django.shortcuts import render
from django.views.generic import ListView, DetailView
import pyrebase

from base.models import Projet


class ProfilDetailView(DetailView):
    model=User
    template_name='base/profil.html'
    slug_field='username'


class ProjetListView(ListView):
    model = Projet
    template_name = 'base/home.html'

