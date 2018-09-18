from django.views.generic import ListView, DetailView
from django_filters.views import FilterView

from avis.filters import RestaurantFilter
from avis.models import Restaurant, Avis, Plat


class RestaurantList(FilterView):
    filterset_class = RestaurantFilter


class RestaurantDetail(DetailView):
    model = Restaurant


class PlatList(ListView):
    model = Plat


class PlatDetail(DetailView):
    model = Plat


class AvisListView(ListView):
    model = Avis
    ordering = '-date_creation'


class AvisDetailView(DetailView):
    model = Avis
