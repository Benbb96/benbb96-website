from django import forms

from tracker.models import Track


class TrackForm(forms.ModelForm):
    class Meta:
        model = Track
        fields = ('commentaire',)
        widgets = {'commentaire': forms.TextInput(attrs={'placeholder': 'Facultatif', 'class': 'form-control'})}
