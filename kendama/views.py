import json
from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.forms import inlineformset_factory, Select, NumberInput
from django.http import JsonResponse, HttpResponseNotFound
from django.shortcuts import render, get_object_or_404, redirect
from django.template.defaultfilters import date
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, UpdateView, CreateView, DeleteView
from django_filters.views import FilterView

from base.models import Profil
from kendama.filters import KendamaTrickFilter, ComboFilter, KendamaFliter, LadderFilter
from kendama.forms import TrickPlayerForm, ComboPlayerForm, KendamaTrickForm, ComboForm, KendamaForm, LadderForm
from kendama.models import KendamaTrick, Combo, TrickPlayer, ComboPlayer, ComboTrick, Kendama, Ladder, LadderCombo


class KendamaTrickList(FilterView):
    filterset_class = KendamaTrickFilter
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
        # Initialise la première fréquence de réussite à "Jamais" par défaut
        self.request.user.profil.trickplayer_set.create(trick=kendama_trick)
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
    filterset_class = ComboFilter
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
    },
    min_num=1,
    validate_min=True
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
            # Initialise la première fréquence de réussite à "Jamais" par défaut
            self.request.user.profil.comboplayer_set.create(combo=combo)
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
        obj_player.frequency = frequency
        obj_player.save()

    return JsonResponse({
        'message': 'La fréquence a bien été mise à jour.',
        'date': date(datetime.now(), 'DATETIME_FORMAT')
    })


def frequency_history(request):
    user_id = request.GET.get('userId')
    if not user_id:
        return HttpResponseNotFound
    user = get_object_or_404(User, id=user_id)
    cls = request.GET.get('cls')
    if cls == 'tricks':
        klass = KendamaTrick
    elif cls == 'combos':
        klass = Combo
    else:
        raise ValueError('cls est incorrect : %s' % cls)
    obj_id = request.GET.get('objId')
    obj = get_object_or_404(klass, id=obj_id)

    params = {}
    if cls == 'tricks':
        player_set = user.profil.trickplayer_set
        params['trick'] = obj
    else:
        player_set = user.profil.comboplayer_set
        params['combo'] = obj

    try:
        obj_player = player_set.get(**params)
    except (TrickPlayer.DoesNotExist, ComboPlayer.DoesNotExist):
        obj_player = None

    return render(request, 'kendama/components/frequency_history.html', {'obj': obj_player})


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


class KendamaUpdate(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Kendama
    form_class = KendamaForm
    success_message = 'Le kendama %(name)s a bien été mis à jour.'

    def get_queryset(self):
        return super().get_queryset().filter(owner=self.request.user.profil)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields.pop('owner')
        return form


class KendamaDelete(LoginRequiredMixin, DeleteView):
    model = Kendama
    success_url = reverse_lazy('kendama:kendamas')

    def get_queryset(self):
        return super().get_queryset().filter(owner=self.request.user.profil)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Le kendama %s a bien été supprimé.' % self.get_object())
        return super().delete(request, *args, **kwargs)


class LadderList(FilterView):
    filterset_class = LadderFilter
    context_object_name = 'ladders'


class LadderDetail(DetailView):
    model = Ladder

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return super().get_queryset().public()
        return super().get_queryset().filter(Q(creator=self.request.user.profil) | Q(private=False))


LadderComboFormSet = inlineformset_factory(
    Ladder,
    LadderCombo,
    fields=('combo', 'order'),
    widgets={
        'order': NumberInput(attrs={'style': 'width: 80px'}),
    },
    min_num=1,
    validate_min=True
)


class LadderCreate(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Ladder
    form_class = LadderForm
    success_message = 'Le ladder %(name)s a bien été créé.'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ladder_combo_formset'] = LadderComboFormSet(self.request.POST or None)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        ladder_combo_formset = context['ladder_combo_formset']
        if ladder_combo_formset.is_valid():
            ladder = form.save(commit=False)
            ladder.creator = self.request.user.profil
            ladder.save()
            ladder_combo_formset.instance = ladder
            ladder_combo_formset.save()
            messages.success(self.request, 'Le ladder %s a bien été créé.' % ladder)
            return redirect(ladder)
        return self.render_to_response(self.get_context_data(form=form))


class LadderUpdate(LoginRequiredMixin, UpdateView):
    model = Ladder
    form_class = LadderForm

    def get_queryset(self):
        return super().get_queryset().filter(creator=self.request.user.profil)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ladder_combo_formset'] = LadderComboFormSet(self.request.POST or None, instance=self.get_object())
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        ladder_combo_formset = context['ladder_combo_formset']
        if ladder_combo_formset.is_valid():
            ladder = form.save()
            ladder_combo_formset.save()
            messages.success(self.request, 'Le ladder %s a bien été mis à jour.' % ladder)
            return redirect(ladder)
        return self.render_to_response(self.get_context_data(form=form))


class LadderDelete(LoginRequiredMixin, DeleteView):
    model = Ladder
    success_url = reverse_lazy('kendama:ladders')

    def get_queryset(self):
        return super().get_queryset().filter(creator=self.request.user.profil)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Le ladder %s a bien été supprimé.' % self.get_object())
        return super().delete(request, *args, **kwargs)


def profil_page(request, username):
    profil = get_object_or_404(Profil, user__username=username)
    player_tricks = profil.trickplayer_set.filter(trick__creator=profil)
    player_combos = profil.comboplayer_set.filter(combo__creator=profil)
    return render(request, 'kendama/profil.html', {
        'profil': profil,
        'player_tricks': player_tricks,
        'player_combos': player_combos
    })
