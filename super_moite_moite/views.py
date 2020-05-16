from django.contrib import messages
from django.shortcuts import render, redirect
from django.views.generic import DetailView

from super_moite_moite.forms import LogementForm
from super_moite_moite.models import Logement


def liste_logements(request):
    form = LogementForm(
        request.POST or None,
        profil=request.user.profil
    )
    if form.is_valid():
        logement = form.save()
        messages.success(request, f'Le logement {logement} a bien été créé.')
        return redirect(logement)

    logements = request.user.profil.logements.prefetch_related('habitants__user')

    return render(request, 'super_moite_moite/logement_list.html', {
        'logements': logements,
        'form': form
    })


class LogementDetailView(DetailView):
    context_object_name = 'logement'
    model = Logement

    def get_queryset(self):
        return self.request.user.profil.logements.all()
