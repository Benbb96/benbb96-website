from django.views.generic import ListView, DetailView

from avis.models import Restaurant, Avis, Plat


class RestaurantList(ListView):
    model = Restaurant


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
