from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string

from my_spot.forms import SpotFilterForm, PublicSpotFilterForm
from my_spot.models import Spot, SpotTag, SpotGroup


def build_data(spots, user):
    """
    Util function to build the data which will be returned in the JsonResponse

    :param spots:
    :param user:
    :return:
    """
    data = []
    for spot in spots:
        data.append({
            'position': {
                'lat': spot.position.latitude,
                'lng': spot.position.longitude
            },
            'nom': spot.nom,
            'visibilite': spot.visibilite,
            'perso': False if not user.is_authenticated else spot.explorateur == user.profil,
            'content': render_to_string('my_spot/maker_info_window.html', {'spot': spot})
        })
    return data


def carte(request, tag_slug=None):
    if request.is_ajax():
        spots = Spot.objects.visible_for_user(request.user)
        # Récupère les paramètres et filtre les spots
        visibilite = request.GET.get('visibilite', None)
        if visibilite and visibilite != '0':
            spots = spots.filter(visibilite=int(visibilite))
        perso = request.GET.get('perso', 'false')
        if perso == 'true':
            spots = spots.filter(explorateur__user=request.user)
        tags = request.GET.getlist('tags[]', None)
        if tags:
            tags = map(int, tags)
            spots = spots.filter(tags__in=tags)
        groupes = request.GET.getlist('groupes[]', None)
        if groupes:
            groupes = map(int, groupes)
            spots = spots.filter(groupes__in=groupes)

        return JsonResponse({'spots': build_data(spots, request.user)})

    tag = None
    if tag_slug:
        tag = get_object_or_404(SpotTag, slug=tag_slug)

    if request.user.is_authenticated:
        form = SpotFilterForm()
        # Filtre les groupes en fonction du user connecté
        form.fields['groupes'].queryset = SpotGroup.objects.filter(profils__user=request.user)
    else:
        form = PublicSpotFilterForm()

    if tag:
        form.initial = {'tags': [tag.id]}

    return render(request, 'my_spot/map.html', {'form': form})


def spot_detail(request, spot_slug):
    spot = get_object_or_404(Spot.objects.visible_for_user(request.user)
        .select_related('explorateur__user')
        .prefetch_related('photos__photographe__user', 'notes__auteur__user', 'tags', 'groupes'), slug=spot_slug)
    return render(request, 'my_spot/spot_detail.html', {
        'spot': spot,
        'groupes': spot.groupes.filter(profils__user=request.user)
    })


@login_required
def spot_group_detail(request, spot_group_slug):
    spot_group = get_object_or_404(
        SpotGroup.objects.filter(profils__user=request.user).prefetch_related('profils__user'),
        slug=spot_group_slug
    )
    if request.is_ajax():
        spots = spot_group.spots.visible_for_user(request.user)
        return JsonResponse({'spots': build_data(spots, request.user)})

    return render(request, 'my_spot/spot_group_detail.html', {'spot_group': spot_group})
