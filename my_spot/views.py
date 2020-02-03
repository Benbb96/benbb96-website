from django.contrib.auth.models import Group
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string

from my_spot.forms import SpotFilterForm
from my_spot.models import Spot, SpotTag


def carte(request, tag_slug=None):
    if request.is_ajax():
        spots = Spot.objects.visible_for_user(request.user)
        # Récupère les paramètres et filtre les spots
        visibilite = request.GET.get('visibilite', None)
        if visibilite and visibilite != '0':
            spots = spots.filter(visibilite=int(visibilite))
        tags = request.GET.getlist('tags[]', None)
        if tags:
            tags = map(int, tags)
            spots = spots.filter(tags__in=tags)
        groupes = request.GET.getlist('groupes[]', None)
        if groupes:
            groupes = map(int, groupes)
            spots = spots.filter(groupes__in=groupes)

        data = []
        for spot in spots:
            data.append({
                'position': {
                    'lat': spot.position.latitude,
                    'lng': spot.position.longitude
                },
                'nom': spot.nom,
                'visibilite': spot.visibilite,
                'perso': False if not request.user.is_authenticated else spot.explorateur == request.user.profil,
                'content': render_to_string('my_spot/maker_info_window.html', {'spot': spot})
            })
        return JsonResponse({'spots': data})

    tag = None
    if tag_slug:
        tag = get_object_or_404(SpotTag, slug=tag_slug)

    form = SpotFilterForm(groupes__user=request.user)
    if not request.user.is_authenticated:
        form.fields.pop('visibilite')
        form.fields.pop('groupes')
    if tag:
        form.initial = {'tags': [tag.id]}

    return render(request, 'my_spot/map.html', {'form': form})


def spot_detail(request, spot_slug):
    spot = get_object_or_404(Spot.objects.visible_for_user(request.user)
        .select_related('explorateur__user')
        .prefetch_related('photos__photographe__user', 'notes__auteur__user', 'tags', 'groupes'), slug=spot_slug)
    return render(request, 'my_spot/spot_detail.html', {'spot': spot})
