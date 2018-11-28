from django import forms

from avis.models import Avis, Produit
from base.widgets import FirebaseUploadWidget


class AvisForm(forms.ModelForm):
    class Meta:
        model = Avis
        fields = '__all__'
        widgets = {'photo': FirebaseUploadWidget(folder='avis')}


class ProduitForm(forms.ModelForm):
    class Meta:
        model = Produit
        fields = '__all__'

    def clean(self):
        if 'categories' in self.cleaned_data:
            structure = self.cleaned_data['structure']
            categories_possible = structure.type.categories.all()
            for categorie in self.cleaned_data['categories'].all():
                if not categorie in categories_possible:
                    raise forms.ValidationError({
                        'categories': 'Vous ne pouvez pas choisir la catégorie %s pour une structure de type %s' %
                                      (categorie, structure)
                    })
