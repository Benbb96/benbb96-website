from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import ListView, TemplateView

from avis.models import Restaurant


class RecommandationIndex(TemplateView):
    template_name = 'avis/index.html'


class RestaurantList(ListView):
    model = Restaurant
