from django.views.generic import ListView, DetailView
from django_filters.views import FilterView

from avis.filters import StructureFilter
from avis.models import Structure, Avis, Plat


class StructureList(FilterView):
    filterset_class = StructureFilter


class StructureDetail(DetailView):
    model = Structure


class PlatList(ListView):
    model = Plat


class PlatDetail(DetailView):
    model = Plat


class AvisListView(ListView):
    model = Avis
    ordering = '-date_creation'


class AvisDetailView(DetailView):
    model = Avis
