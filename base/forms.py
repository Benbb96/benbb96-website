from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, label='Prénom', required=False, help_text='Optionnel.')
    last_name = forms.CharField(max_length=30, label='Nom', required=False, help_text='Optionnel.')
    email = forms.EmailField(max_length=254, help_text='Requis.')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', )
