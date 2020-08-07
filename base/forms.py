from django import forms
from django.contrib.auth.forms import UserCreationForm, UsernameField
from django.contrib.auth.models import User

from base.fields import MyDateField
from base.models import Profil


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, label='Prénom', required=False, help_text='Optionnel.')
    last_name = forms.CharField(max_length=30, label='Nom', required=False, help_text='Optionnel.')
    email = forms.EmailField(max_length=254, help_text='Requis.')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', )


class ProfilForm(forms.ModelForm):
    username = UsernameField(label="Nom d'utilisateur")
    first_name = forms.CharField(max_length=30, label='Prénom', required=False)
    last_name = forms.CharField(max_length=30, label='Nom', required=False)
    email = forms.EmailField(max_length=254)
    birthday = MyDateField(label='Date anniversaire', required=False)

    class Meta:
        model = Profil
        fields = ('username', 'first_name', 'last_name', 'email', 'avatar', 'birthday')
