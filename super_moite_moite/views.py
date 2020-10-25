from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import DetailView, UpdateView, DeleteView
from django.contrib.auth.decorators import login_required


from super_moite_moite.forms import LogementForm
from super_moite_moite.models import Logement
from super_moite_moite.serializers import LogementSerializer


@login_required
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Envoi également le JSON du logement avec toutes les infos qui vont être utilisés par Vue
        context['json'] = LogementSerializer(self.object).data
        return context


class LogementUpdateView(UpdateView):
    context_object_name = 'logement'
    model = Logement
    form_class = LogementForm

    def get_queryset(self):
        return self.request.user.profil.logements.all()

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['profil'] = self.request.user.profil
        return kwargs


class LogementDeleteView(DeleteView):
    context_object_name = 'logement'
    model = Logement
    success_url = reverse_lazy('super-moite-moite:liste-logements')

    def get_queryset(self):
        return self.request.user.profil.logements.all()


@login_required
def dupliquer_logement(request, slug):
    logement = get_object_or_404(request.user.profil.logements.all(), slug=slug)
    # Copie du logement
    duplicata_logement = Logement.objects.create(
        nom='Copie de ' + logement.nom
    )
    # Ajout des habitants
    for habitant in logement.habitants.all():
        duplicata_logement.habitants.add(habitant)
    # Copie des Catégories
    for categorie in logement.categories.all():
        duplicata_categorie = duplicata_logement.categories.create(
            nom=categorie.nom,
            order=categorie.order,
            couleur=categorie.couleur
        )
        # Copie des tâches de la catégorie
        for tache in categorie.taches.all():
            duplicata_tache = duplicata_categorie.taches.create(
                nom=tache.nom,
                description=tache.description,
                order=tache.order,
                photo=tache.photo
            )
            # Copie des points par défaut
            for point_defaut in tache.point_profils.all():
                duplicata_tache.point_profils.create(
                    profil=point_defaut.profil,
                    point=point_defaut.point
                )

    messages.success(request, 'Le logement %s a bien été dupliqué.' % logement)
    return redirect(duplicata_logement)
