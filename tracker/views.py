from django.views.generic import ListView, DetailView

from tracker.models import Tracker


class TrackerListView(ListView):
    model = Tracker


class TrackerDetailView(DetailView):
    model = Tracker
