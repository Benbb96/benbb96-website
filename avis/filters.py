import django_filters
from django import forms
from django_filters.widgets import SuffixedMultiWidget

from avis.models import CategorieProduit, Produit, Structure, TypeStructure
from base.widgets import TomSelectMultipleWidget


class PriceRangeWidget(SuffixedMultiWidget):
    """RangeWidget de django_filters, avec des <input type=number> à placeholder
    distinct (min/max) au lieu de deux <input type=text> identiques."""

    template_name = "django_filters/widgets/multiwidget.html"
    suffixes = ["min", "max"]

    def __init__(self, attrs=None):
        widgets = (
            forms.NumberInput(attrs={"placeholder": "Min €", "min": 0, "step": "0.01"}),
            forms.NumberInput(attrs={"placeholder": "Max €", "min": 0, "step": "0.01"}),
        )
        super().__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            return [value.start, value.stop]
        return [None, None]


class StructureFilter(django_filters.FilterSet):
    nom = django_filters.CharFilter(lookup_expr="icontains", label="Nom")
    informations = django_filters.CharFilter(
        lookup_expr="icontains", label="Informations"
    )
    type = django_filters.ModelChoiceFilter(
        lookup_expr="exact",
        queryset=TypeStructure.objects.all(),
        label="Type structure",
    )

    class Meta:
        model = Structure
        fields = ("nom", "informations", "type")


class ProduitFilter(django_filters.FilterSet):
    nom = django_filters.CharFilter(lookup_expr="icontains", label="Nom")
    categories = django_filters.ModelMultipleChoiceFilter(
        lookup_expr="exact",
        label="Catégories",
        queryset=CategorieProduit.objects.all(),
        widget=TomSelectMultipleWidget(placeholder="Catégories"),
    )
    prix = django_filters.RangeFilter(widget=PriceRangeWidget())

    class Meta:
        model = Produit
        fields = ("nom", "categories", "prix")
