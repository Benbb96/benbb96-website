from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView

from tracker.forms import TrackForm
from tracker.models import Tracker


class TrackerListView(ListView):
    model = Tracker

    def get_queryset(self):
        queryset = super(TrackerListView, self).get_queryset()
        return queryset.filter(createur=self.request.user.profil)


def tracker_detail(request, slug):
    tracker = get_object_or_404(Tracker, slug=slug)
    form = TrackForm(request.POST or None)
    if form.is_valid():
        track = form.save(commit=False)
        track.tracker = tracker
        track.save()
        return redirect('tracker:detail-tracker', slug=tracker.slug)
    return render(request, 'tracker/tracker_detail.html', {
        'tracker': tracker,
        'form': form
    })