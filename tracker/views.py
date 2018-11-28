from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.views.generic import ListView
from django_pandas.io import read_frame
import pandas as pd

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

    # Regroupe les données par date pour faire des stats
    df = read_frame(tracker.tracks.all(), fieldnames=['datetime'])
    df['datetime'] = pd.to_datetime(df['datetime'])
    df.index = df['datetime']
    df['count'] = [1] * tracker.tracks.count()
    data = df.resample('D').sum()
    data.index = data.index.strftime('%d/%m/%y')

    delta = timezone.now().date() - tracker.tracks.earliest('datetime').datetime.date()

    return render(request, 'tracker/tracker_detail.html', {
        'tracker': tracker,
        'form': form,
        'data': data,
        'avg': tracker.tracks.count() / (delta.days + 1)  # On ajoute un jour pour éviter la division par 0
    })