import json
from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.forms import inlineformset_factory
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.template.defaultfilters import date
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, UpdateView, CreateView, DeleteView
from django_filters.views import FilterView

from kendama.filters import KendamaTrickFliter, ComboFliter
from kendama.forms import TrickPlayerForm, ComboPlayerForm, KendamaTrickForm, ComboForm
from kendama.models import KendamaTrick, Combo, TrickPlayer, ComboPlayer, ComboTrick


class KendamaTrickList(FilterView):
    filterset_class = KendamaTrickFliter
    context_object_name = 'tricks'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['form'] = KendamaTrickForm()
        return context


class KendamaTrickDetail(DetailView):
    model = KendamaTrick

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            try:
                authenticated_trick_player = self.request.user.profil.trickplayer_set.get(trick=self.get_object())
            except TrickPlayer.DoesNotExist:
                authenticated_trick_player = None
            context['authenticated_user_frequency'] = authenticated_trick_player
            context['form'] = TrickPlayerForm(instance=authenticated_trick_player)
        return context


class KendamaTrickCreate(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = KendamaTrick
    form_class = KendamaTrickForm
    success_message = 'Le trick %(name)s a bien été créé.'

    def form_valid(self, form):
        kendama_trick = form.save(commit=False)
        kendama_trick.creator = self.request.user.profil
        kendama_trick.save()
        return redirect(kendama_trick)


class KendamaTrickUpdate(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = KendamaTrick
    form_class = KendamaTrickForm
    success_message = 'Le trick %(name)s a bien été mis à jour.'


class KendamaTrickDelete(LoginRequiredMixin, DeleteView):
    model = KendamaTrick
    success_url = reverse_lazy('kendama:tricks')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Le trick %s a bien été supprimé.' % self.get_object())
        return super().delete(request, *args, **kwargs)


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
    return JsonResponse({
        'message': 'La fréquence a bien été mise à jour !',
        'date': date(datetime.now(), 'DATETIME_FORMAT')
    })


class ComboList(FilterView):
    filterset_class = ComboFliter
    context_object_name = 'combos'


class ComboDetail(DetailView):
    model = Combo

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            try:
                authenticated_combo_player = self.request.user.profil.comboplayer_set.get(combo=self.get_object())
            except ComboPlayer.DoesNotExist:
                authenticated_combo_player = None
            context['authenticated_user_frequency'] = authenticated_combo_player
            context['form'] = ComboPlayerForm(instance=authenticated_combo_player)
        return context


ComboTrickFormSet = inlineformset_factory(Combo, ComboTrick, fields=('trick', 'order'))


class ComboUpdate(LoginRequiredMixin, UpdateView):
    model = Combo
    form_class = ComboForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['combo_trick_formset'] = ComboTrickFormSet(self.request.POST or None, instance=self.get_object())
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        combo_trick_formset = context['combo_trick_formset']
        if combo_trick_formset.is_valid():
            self.object = form.save()
            combo_trick_formset.save()
            messages.success(self.request, 'Le combo %s a bien été mis à jour.' % self.object)
            return redirect(self.object)
        return self.render_to_response(self.get_context_data(form=form))


class ComboDelete(LoginRequiredMixin, DeleteView):
    model = Combo
    success_url = reverse_lazy('kendama:combos')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Le combo %s a bien été supprimé.' % self.get_object())
        return super().delete(request, *args, **kwargs)


@login_required
@require_POST
def update_combo_player_frequency(request, combo_id):
    combo = get_object_or_404(Combo, id=combo_id)
    json_data = json.loads(request.body)
    frequency = json_data.get('frequency')
    if not frequency:
        return JsonResponse({'message': 'Veuillez renseigner la fréquence'}, status=422)
    combo_player, created = request.user.profil.comboplayer_set.get_or_create(
        combo=combo, defaults={'frequency': frequency}
    )
    if not created:
        combo_player.frequency = frequency
        combo_player.save()
    return JsonResponse({
        'message': 'La fréquence a bien été mise à jour !',
        'date': date(datetime.now(), 'DATETIME_FORMAT')
    })
