from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.forms import inlineformset_factory, NumberInput
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django_select2.forms import ModelSelect2Widget

from versus.models import Jeu, Joueur, Partie, PartieJoueur


class JeuListView(ListView):
    model = Jeu


class JoueurListView(ListView):
    model = Joueur


class JeuDetailView(DetailView):
    model = Jeu
    slug_field = 'slug'
    queryset = Jeu.objects.select_related('createur__user').prefetch_related('parties__partiejoueur_set__joueur')


class JoueurDetailView(DetailView):
    model = Joueur
    slug_field = 'slug'
    queryset = Joueur.objects.select_related('profil__user').prefetch_related(
        'partie_set__jeu', 'partie_set__partiejoueur_set__joueur',
        'partiejoueur_set__partie__jeu', 'partiejoueur_set__partie__partiejoueur_set',
    )


PartieJoueurFormSet = inlineformset_factory(
    Partie,
    PartieJoueur,
    fields=('joueur', 'score_classement'),
    widgets={
        'joueur': ModelSelect2Widget(
            model=Joueur,
            search_fields=['nom__icontains', 'profil__user__username__icontains'],
            attrs={'style': 'width: 100%', 'data-minimum-input-length': 0}
        ),
        'score_classement': NumberInput(attrs={'class': 'form-control'})
    },
    can_delete=False
)


@permission_required('versus.add_partie')
def ajout_partie(request, slug):
    jeu = get_object_or_404(Jeu, slug=slug)
    partie = Partie(jeu=jeu)
    formset = PartieJoueurFormSet(request.POST or None, instance=partie)
    if formset.is_valid():
        partie.save()
        formset.save()
        messages.success(request, 'La nouvelle partie de %s a bien été ajouté.' % jeu)
        return redirect(jeu)
    return render(request, 'versus/partie_form.html', {'jeu': jeu, 'formset': formset})


@permission_required('versus.change_partie')
def edition_partie(request, slug, partie_id):
    jeu = get_object_or_404(Jeu, slug=slug)
    partie = get_object_or_404(Partie, id=partie_id)
    formset = PartieJoueurFormSet(request.POST or None, instance=partie)
    if formset.is_valid():
        formset.save()
        messages.success(request, 'La partie de %s a bien été mise à jour.' % jeu)
        return redirect(jeu)
    return render(request, 'versus/partie_form.html', {'jeu': jeu, 'partie': partie, 'formset': formset})


@permission_required('versus.delete_partie')
def suppression_partie(request, slug, partie_id):
    jeu = get_object_or_404(Jeu, slug=slug)
    partie = get_object_or_404(Partie, id=partie_id)
    if request.method == 'POST':
        partie.delete()
        messages.success(request, 'La partie de %s a bien été supprimée.' % jeu)
        return redirect(jeu)
    return render(request, 'versus/partie_confirm_delete.html', {'jeu': jeu, 'partie': partie})


