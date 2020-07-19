import json
from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.forms import inlineformset_factory, Select, NumberInput
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.template.defaultfilters import date
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, UpdateView, CreateView, DeleteView
from django_filters.views import FilterView

from kendama.filters import KendamaTrickFliter, ComboFliter, KendamaFliter
from kendama.forms import TrickPlayerForm, ComboPlayerForm, KendamaTrickForm, ComboForm, KendamaForm
from kendama.models import KendamaTrick, Combo, TrickPlayer, ComboPlayer, ComboTrick, Kendama


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

    def get_queryset(self):
        return super().get_queryset().filter(creator=self.request.user.profil)


class KendamaTrickDelete(LoginRequiredMixin, DeleteView):
    model = KendamaTrick
    success_url = reverse_lazy('kendama:tricks')

    def get_queryset(self):
        return super().get_queryset().filter(creator=self.request.user.profil)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Le trick %s a bien été supprimé.' % self.get_object())
        return super().delete(request, *args, **kwargs)


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


ComboTrickFormSet = inlineformset_factory(
    Combo,
    ComboTrick,
    fields=('trick', 'order'),
    widgets={
        'trick': Select(attrs={'class': 'trickSelect'}),
        'order': NumberInput(attrs={'style': 'width: 80px'}),
    }
)


class ComboCreate(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Combo
    form_class = ComboForm
    success_message = 'Le combo %(name)s a bien été créé.'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['combo_trick_formset'] = ComboTrickFormSet(self.request.POST or None)
        context['trick_form'] = KendamaTrickForm(self.request.POST or None, prefix='trick')
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        combo_trick_formset = context['combo_trick_formset']
        if combo_trick_formset.is_valid():
            combo = form.save(commit=False)
            combo.creator = self.request.user.profil
            combo.save()
            combo_trick_formset.instance = combo
            combo_trick_formset.save()
            messages.success(self.request, 'Le combo %s a bien été créé.' % combo)
            return redirect(combo)
        return self.render_to_response(self.get_context_data(form=form))


class ComboUpdate(LoginRequiredMixin, UpdateView):
    model = Combo
    form_class = ComboForm

    def get_queryset(self):
        return super().get_queryset().filter(creator=self.request.user.profil)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['combo_trick_formset'] = ComboTrickFormSet(self.request.POST or None, instance=self.get_object())
        context['trick_form'] = KendamaTrickForm(self.request.POST or None, prefix='trick')
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        combo_trick_formset = context['combo_trick_formset']
        if combo_trick_formset.is_valid():
            combo = form.save()
            combo_trick_formset.save()
            messages.success(self.request, 'Le combo %s a bien été mis à jour.' % combo)
            return redirect(combo)
        return self.render_to_response(self.get_context_data(form=form))


class ComboDelete(LoginRequiredMixin, DeleteView):
    model = Combo
    success_url = reverse_lazy('kendama:combos')

    def get_queryset(self):
        return super().get_queryset().filter(creator=self.request.user.profil)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Le combo %s a bien été supprimé.' % self.get_object())
        return super().delete(request, *args, **kwargs)


@login_required
@require_POST
def update_player_frequency(request, cls, obj_id):
    if cls == 'tricks':
        klass = KendamaTrick
    elif cls == 'combos':
        klass = Combo
    else:
        raise ValueError('cls est incorrect : %s' % cls)
    obj = get_object_or_404(klass, id=obj_id)

    json_data = json.loads(request.body)
    frequency = json_data.get('frequency')
    if not frequency:
        return JsonResponse({'message': 'Veuillez renseigner la fréquence'}, status=422)

    params = {'defaults': {'frequency': frequency}}
    if cls == 'tricks':
        player_set = request.user.profil.trickplayer_set
        params['trick'] = obj
    else:
        player_set = request.user.profil.comboplayer_set
        params['combo'] = obj

    obj_player, created = player_set.get_or_create(**params)
    if not created:
        obj.frequency = frequency
        obj.save()

    return JsonResponse({
        'message': 'La fréquence a bien été mise à jour.',
        'date': date(datetime.now(), 'DATETIME_FORMAT')
    })


@require_POST
@login_required
def create_trick_from_modal(request):
    form = KendamaTrickForm(request.POST, prefix='trick')
    if form.is_valid():
        trick = form.save(commit=False)
        trick.creator = request.user.profil
        trick.save()
        return JsonResponse({'success': True, 'id': trick.id, 'name': trick.name})
    return JsonResponse({'success': False, 'message': 'Il y a des erreurs dans le formulaire', 'errors': form.errors})


class KendamaList(FilterView):
    filterset_class = KendamaFliter
    context_object_name = 'kendamas'


class KendamaDetail(DetailView):
    model = Kendama


class KendamaCreate(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Kendama
    form_class = KendamaForm
    success_message = 'Le kendama %(name)s a bien été créé.'

    def form_valid(self, form):
        kendama = form.save(commit=False)
        kendama.owner = self.request.user.profil
        kendama.save()
        return redirect('kendama:kendamas')  # TODO redirect to kendama

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields.pop('owner')
        return form
