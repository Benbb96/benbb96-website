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


class AvisDetailView(DetailView):
    model = Avis
