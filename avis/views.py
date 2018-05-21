from django.views.generic import ListView, DetailView

from avis.models import Restaurant, Avis


class AvisListView(ListView):
    model = Avis


class AvisDetailView(DetailView):
    model = Avis


class RestaurantList(ListView):
    model = Restaurant
