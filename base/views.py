from django.views.generic import ListView

from base.models import Projet


class ProjetListView(ListView):
    model = Projet
    template_name = 'base/home.html'
