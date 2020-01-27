from django.contrib.auth.models import Group
from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string

from my_spot.forms import SpotFilterForm
from my_spot.models import Spot


def carte(request):
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
                'perso': spot.explorateur == request.user.profil,
                'content': render_to_string('my_spot/maker_info_window.html', {'spot': spot})
            })
        return JsonResponse({'spots': data})

    form = SpotFilterForm(groupes=Group.objects.filter(user=request.user))

    return render(request, 'my_spot/map.html', {'form': form})
