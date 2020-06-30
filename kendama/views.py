from django.shortcuts import render
from django_filters.views import FilterView

from kendama.filters import KendamaTrickFliter, ComboFliter


class KendamaTrickList(FilterView):
    filterset_class = KendamaTrickFliter
    context_object_name = 'tricks'


class ComboList(FilterView):
    filterset_class = ComboFliter
    context_object_name = 'combos'
