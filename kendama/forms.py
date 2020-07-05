from django import forms

from base.widgets import FirebaseUploadWidget
from kendama.models import Kendama, TrickPlayer, ComboPlayer, KendamaTrick, Combo


class KendamaForm(forms.ModelForm):
    class Meta:
        model = Kendama
        fields = '__all__'
        widgets = {'photo': FirebaseUploadWidget(folder='kendamas')}


class KendamaTrickForm(forms.ModelForm):
    class Meta:
        model = KendamaTrick
        exclude = ('slug', 'creator', 'players')
        widgets = {
            'tutorial_video_link': forms.TextInput(attrs={'class': 'input-block'})
        }


class ComboForm(forms.ModelForm):
    class Meta:
        model = Combo
        exclude = ('slug', 'creator', 'players', 'tricks')
        widgets = {
            'tutorial_video_link': forms.TextInput(attrs={'class': 'input-block'}),
        }


class TrickPlayerForm(forms.ModelForm):
    frequency = forms.ChoiceField(
        choices=tuple([('', '------')] + list(TrickPlayer.FREQUENCY))
    )

    class Meta:
        model = TrickPlayer
        fields = ('frequency',)


class ComboPlayerForm(forms.ModelForm):
    frequency = forms.ChoiceField(
        choices=tuple([('', '------')] + list(ComboPlayer.FREQUENCY))
    )

    class Meta:
        model = ComboPlayer
        fields = ('frequency',)
