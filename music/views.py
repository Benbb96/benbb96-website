from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.generic import ListView, DetailView

from music.models import Playlist, Musique, Lien, Artiste


class PlaylistListView(ListView):
    model = Playlist


class PlaylistDetailView(DetailView):
    model = Playlist
    slug_field = 'slug'


class MusiqueDetailView(DetailView):
    model = Musique
    slug_field = 'slug'
    query_pk_and_slug = True


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
