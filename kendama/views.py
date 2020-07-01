import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST
from django.views.generic import DetailView
from django_filters.views import FilterView

from kendama.filters import KendamaTrickFliter, ComboFliter
from kendama.forms import TrickPlayerForm
from kendama.models import KendamaTrick, Combo, TrickPlayer


class KendamaTrickList(FilterView):
    filterset_class = KendamaTrickFliter
    context_object_name = 'tricks'


class KendamaTrickDetail(DetailView):
    model = KendamaTrick

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            try:
                authenticated_trick_player = self.request.user.profil.trickplayer_set.get(trick=self.get_object())
            except TrickPlayer.DoesNotExist:
                authenticated_trick_player = None
            context['authenticated_trick_player'] = authenticated_trick_player
            context['trick_player_form'] = TrickPlayerForm(instance=authenticated_trick_player)
        return context


@login_required
@require_POST
def update_trick_player_frequency(request, trick_id):
    trick = get_object_or_404(KendamaTrick, id=trick_id)
    json_data = json.loads(request.body)
    frequency = json_data.get('frequency')
    if not frequency:
        return JsonResponse({'message': 'Veuillez renseigner la fréquence'}, status=422)
    trick_player, created = request.user.profil.trickplayer_set.get_or_create(
        trick=trick, defaults={'frequency': frequency}
    )
    if not created:
        trick_player.frequency = frequency
        trick_player.save()
    return JsonResponse({'message': 'La fréquence a bien été mise à jour !'})


class ComboList(FilterView):
    filterset_class = ComboFliter
    context_object_name = 'combos'


class ComboDetail(DetailView):
    model = Combo
