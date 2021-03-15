from django.contrib import messages
from django.contrib.auth import update_session_auth_hash, authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.core.mail import mail_admins
from django.shortcuts import redirect, render, get_object_or_404
from django.utils.safestring import mark_safe
from django.views.generic import ListView, DetailView

from base.forms import SignUpForm, ProfilForm
from base.models import Projet, Profil


def signup(request):
    form = SignUpForm(request.POST or None)
    if form.is_valid():
        form.save()
        username = form.cleaned_data.get('username')
        raw_password = form.cleaned_data.get('password1')
        user = authenticate(username=username, password=raw_password)
        login(request, user)
        messages.success(request, 'Votre compte a bien été créé !')
        user.refresh_from_db()
        mail_admins(
            'Nouveau compte créé !',
            '{} vient de se créer un compte sur mon site : https://www.benbb96.com{}'.format(
                username, user.profil.get_absolute_url()
            ),
        )
        return redirect('base:home')
    return render(request, 'registration/signup.html', {'form': form})


class UserDetailView(DetailView):
    model = User
    template_name_field = 'user'
    template_name = 'base/profil/profil.html'
    slug_field = 'username'

    def get_queryset(self):
        queryset = super(UserDetailView, self).get_queryset()
        return queryset.prefetch_related(
            'profil__joueur__partie_set__partiejoueur_set__joueur', 'profil__joueur__partie_set__jeu',
            'profil__musiques_crees__artiste', 'profil__musiques_crees__featuring', 'profil__musiques_crees__remixed_by'
        )


@login_required
def change_password(request):
    form = PasswordChangeForm(request.user, request.POST or None)
    if form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)
        messages.success(request, 'Votre mot de passe a bien été mis à jour !')
        return redirect('base:change_password')
    elif request.POST:
        messages.error(request, 'Merci de corriger les erreurs ci-dessous.')
    return render(request, 'base/profil/change_password.html', {
        'form': form
    })


@login_required
def update_profil(request, username):
    profil = get_object_or_404(Profil, user__username=username)
    if request.user != profil.user and not request.user.is_superuser:
        raise PermissionDenied

    form = ProfilForm(data=request.POST or None, instance=profil, files=request.FILES or None, initial={
        'username': profil.user.username,
        'first_name': profil.user.first_name,
        'last_name': profil.user.last_name,
        'email': profil.user.email,
    })
    if form.is_valid():
        profil = form.save()
        profil.user.username = form.cleaned_data.get('username')
        profil.user.first_name = form.cleaned_data.get('first_name')
        profil.user.last_name = form.cleaned_data.get('last_name')
        profil.user.email = form.cleaned_data.get('email')
        profil.user.save()
        messages.success(request, 'Votre profil a bien été mis à jour !')
        return redirect(profil)

    return render(request, 'base/profil/update_profil.html', {
        'profil': profil,
        'form': form
    })


class ProjetListView(ListView):
    model = Projet
    template_name = 'base/home.html'

    def get_queryset(self):
        """ If the user isn't authenticated or staff, exclude the private projects """
        qs = super(ProjetListView, self).get_queryset()
        if not self.request.user.is_authenticated:
            qs = qs.exclude(logged_only=True)
        elif not self.request.user.is_staff:
            qs = qs.exclude(staff_only=True)
        return qs
