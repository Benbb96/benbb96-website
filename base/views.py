from django.contrib.auth.models import User
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, DetailView

from base.models import Projet


class UserDetailView(DetailView):
    model = User
    template_name_field = 'user'
    template_name = 'base/profil.html'
    slug_field = 'username'

    def get_queryset(self):
        queryset = super(UserDetailView, self).get_queryset()
        return queryset.prefetch_related(
            'profil__joueur__partie_set__partiejoueur_set__joueur', 'profil__joueur__partie_set__jeu',
            'profil__musiques_crees__artiste', 'profil__musiques_crees__featuring', 'profil__musiques_crees__remixed_by'
        )


class ProjetListView(ListView):
    model = Projet
    template_name = 'base/home.html'


@csrf_exempt
def test_notification(request):
    print(request.POST)
    return HttpResponse('OK')
