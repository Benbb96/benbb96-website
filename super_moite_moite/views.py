from django.views.generic import ListView, DetailView

from super_moite_moite.models import Logement


class LogementListView(ListView):
    context_object_name = 'logements'
    model = Logement

    def get_queryset(self):
        return self.request.user.profil.logements.all()


class LogementDetailView(DetailView):
    context_object_name = 'logement'
    model = Logement

    def get_queryset(self):
        return self.request.user.profil.logements.all()
