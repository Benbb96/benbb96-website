from django.views.generic import ListView, DetailView
from django_filters.views import FilterView

from avis.filters import StructureFilter, ProduitFilter
from avis.models import Structure, Avis, Produit, CategorieProduit


class CategorieProduitDetail(DetailView):
    model = CategorieProduit


class StructureList(FilterView):
    filterset_class = StructureFilter
    context_object_name = 'structures'
    paginate_by = 10


class StructureDetail(DetailView):
    model = Structure


class ProduitList(FilterView):
    filterset_class = ProduitFilter
    context_object_name = 'produits'
    paginate_by = 30


class ProduitDetail(DetailView):
    model = Produit


class AvisListView(ListView):
    model = Avis
    ordering = '-date_creation'

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return super(AvisListView, self).get_queryset()
        return super(AvisListView, self).get_queryset().exclude(prive=True)


class AvisDetailView(DetailView):
    model = Avis
