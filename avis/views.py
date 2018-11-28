from django.views.generic import ListView, DetailView
from django_filters.views import FilterView

from avis.filters import StructureFilter
from avis.models import Structure, Avis, Produit, CategorieProduit


class CategorieProduitDetail(DetailView):
    model = CategorieProduit


class StructureList(FilterView):
    filterset_class = StructureFilter


class StructureDetail(DetailView):
    model = Structure


class ProduitList(ListView):
    model = Produit


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
