from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string

from my_spot.models import Spot


def map(request):
    if request.is_ajax():
        data = []
        for spot in Spot.objects.visible_for_user(request.user):
            data.append({
                'position': {
                    'lat': spot.position.latitude,
                    'lng': spot.position.longitude
                },
                'nom': spot.nom,
                'content': render_to_string('my_spot/maker_info_window.html', {'spot': spot})
            })
        return JsonResponse({'spots': data})

    return render(request, 'my_spot/map.html')
