import django_filters

from avis.models import Structure, TypeStructure, Produit, CategorieProduit


class StructureFilter(django_filters.FilterSet):
    nom = django_filters.CharFilter(lookup_expr='icontains', label='Nom')
    informations = django_filters.CharFilter(lookup_expr='icontains', label='Informations')
    type = django_filters.ModelChoiceFilter(
        lookup_expr='exact', queryset=TypeStructure.objects.all(), label='Type structure',
    )

    class Meta:
        model = Structure
        fields = ('nom', 'informations', 'type')


class ProduitFilter(django_filters.FilterSet):
    nom = django_filters.CharFilter(lookup_expr='icontains', label='Nom')
    categories = django_filters.ModelMultipleChoiceFilter(
        lookup_expr='exact', label='Catégories', queryset=CategorieProduit.objects.all()
    )
    prix = django_filters.RangeFilter()

    class Meta:
        model = Produit
        fields = ('nom', 'categories', 'prix')
