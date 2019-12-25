from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.generic import ListView, DetailView
from django.views.generic.edit import FormMixin

from music.models import Playlist, Musique, Lien, Artiste
from music.templates.music.forms import LienForm


class PlaylistListView(ListView):
    model = Playlist


class PlaylistDetailView(DetailView):
    model = Playlist
    slug_field = 'slug'


class MusiqueDetailView(FormMixin, DetailView):
    model = Musique
    slug_field = 'slug'
    query_pk_and_slug = True
    form_class = LienForm

    def get_context_data(self, **kwargs):
        context = super(MusiqueDetailView, self).get_context_data(**kwargs)
        context['form'] = self.get_form()
        return context

    def post(self, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        lien = form.save(commit=False)
        lien.musique = self.object
        if self.request.user.profil:
            lien.createur = self.request.user.profil
            # Son lien est automatiquement validé si c'est la musique qu'il a créé
            if self.request.user == self.object.createur.user:
                lien.date_validation = timezone.now()
        lien.save()
        messages.success(self.request, 'Le lien a bien été ajouté.')
        return redirect(self.object.get_absolute_url())


class ArtisteDetailView(DetailView):
    model = Artiste
    slug_field = 'slug'


@require_POST
def incremente_link_click_count(request, lien_id):
    lien = get_object_or_404(Lien, id=lien_id)
    lien.click_count += 1
    lien.save(update_fields=['click_count'])
    return JsonResponse({'success': True, 'click_count': lien.click_count})


def valider_lien(request, lien_id):
    lien = get_object_or_404(Lien, id=lien_id)
    if request.user != lien.musique.createur.user or not request.user.is_superuser:
        messages.error(request, "Cette musique ne t'appartient pas.")
    else:
        lien.date_validation = timezone.now()
        lien.save(update_fields=['date_validation'])
    return redirect(lien.musique.get_absolute_url())
