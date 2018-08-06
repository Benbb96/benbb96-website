from django.views.generic import ListView, DetailView

from avis.models import Restaurant, Avis


class AvisListView(ListView):
    model = Avis
    ordering = '-date_creation'


class AvisDetailView(DetailView):
    model = Avis


class RestaurantList(ListView):
    model = Restaurant


class RestaurantDetail(DetailView):
    model = Restaurant
