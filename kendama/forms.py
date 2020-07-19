from django import forms

from base.widgets import FirebaseUploadWidget
from kendama.models import Kendama, TrickPlayer, ComboPlayer, KendamaTrick, Combo, Ladder


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
            'description': forms.Textarea(attrs={'rows': 4}),
            'tutorial_video_link': forms.URLInput(attrs={'class': 'input-block'})
        }


class ComboForm(forms.ModelForm):
    class Meta:
        model = Combo
        exclude = ('slug', 'creator', 'players', 'tricks')
        widgets = {
            'tutorial_video_link': forms.URLInput(attrs={'class': 'input-block'}),
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


class LadderForm(forms.ModelForm):
    class Meta:
        model = Ladder
        exclude = ('slug', 'creator', 'players', 'combos')
        widgets = {
            'tutorial_video_link': forms.URLInput(attrs={'class': 'input-block'}),
        }
