from django.shortcuts import render
from django.views.generic import DetailView
from django_filters.views import FilterView

from kendama.filters import KendamaTrickFliter, ComboFliter
from kendama.models import KendamaTrick, Combo


class KendamaTrickList(FilterView):
    filterset_class = KendamaTrickFliter
    context_object_name = 'tricks'


class KendamaTrickDetail(DetailView):
    model = KendamaTrick


class ComboList(FilterView):
    filterset_class = ComboFliter
    context_object_name = 'combos'


class ComboDetail(DetailView):
    model = Combo
