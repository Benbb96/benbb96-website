from datetime import datetime, timedelta

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.timezone import make_aware, make_naive
from django.views.decorators.http import require_POST
from django.views.generic import UpdateView, DeleteView
from django_pandas.io import read_frame
import pandas as pd
from rest_framework import generics

from tracker.forms import TrackForm, TrackerForm
from tracker.models import Tracker, Track
from tracker.serializers import TrackSerializer


@login_required
def tracker_list(request):
    trackers = Tracker.objects.filter(createur=request.user.profil)

    form = TrackerForm(request.POST or None)
    if form.is_valid():
        if request.user.profil.trackers.filter(nom=form.cleaned_data['nom']).exists():
            form.add_error('nom', 'Vous avez déjà créé un tracker du même nom.')
        else:
            tracker = form.save(commit=False)
            tracker.createur = request.user.profil
            tracker.save()

            return redirect('tracker:liste-tracker')

    return render(request, 'tracker/tracker_list.html', {'trackers': trackers, 'form': form})


class TrackerUpdateView(UpdateView):
    model = Tracker
    form_class = TrackerForm


class TrackerDeleteView(DeleteView):
    model = Tracker
    success_url = reverse_lazy('tracker:liste-tracker')


@login_required
def tracker_detail(request, pk):
    tracker = get_object_or_404(Tracker.objects.filter(createur=request.user.profil), id=pk)

    form = TrackForm(request.POST or None, initial={'datetime': timezone.now()})
    if form.is_valid():
        track = form.save(commit=False)
        track.tracker = tracker
        track.save()
        return redirect(tracker)

    tracks = tracker.tracks.all()
    for track in tracks:
        track.form = TrackForm(instance=track)

    return render(request, 'tracker/tracker_detail.html', {
        'tracker': tracker,
        'tracks': tracks,
        'form': form
    })


class TrackUpdateView(generics.UpdateAPIView):
    queryset = Track.objects.all()
    serializer_class = TrackSerializer


class TrackDeleteView(generics.DestroyAPIView):
    queryset = Track.objects.all()
    serializer_class = TrackSerializer


def get_tracks_from_request(request):
    tracker = get_object_or_404(Tracker.objects.filter(createur=request.user.profil), id=request.POST.get('id'))

    start = request.POST.get('start', None)
    end = request.POST.get('end', None)

    tracks = tracker.tracks.all()
    if start:
        start = make_aware(datetime.strptime(start, '%y-%m-%d %H:%M:%S'))
        tracks = tracks.filter(datetime__gte=start)
    if end:
        end = make_aware(datetime.strptime(end, '%y-%m-%d %H:%M:%S'))
        tracks = tracks.filter(datetime__lte=end)

    return tracks


@require_POST
def tracker_data(request):
    if not request.is_ajax():
        return JsonResponse({'error': 'Unauthorized access'}, status=401)

    tracks = get_tracks_from_request(request)

    labels = []
    data = []
    avg = 0

    if tracks.exists():
        # Regroupe les données par date pour faire des stats
        frequency = request.POST.get('frequency', 'D')
        df = read_frame(tracks, fieldnames=['datetime'])
        df['datetime'] = pd.to_datetime(df['datetime'])
        df['datetime'] = df['datetime'].dt.tz_convert('Europe/Paris')
        df.index = df['datetime']
        df['count'] = [1] * tracks.count()
        data = df.resample(frequency).sum()

        delta = timezone.now().date() - tracks.earliest('datetime').datetime.date()

        format = '%d/%m/%y'
        avg = tracks.count() / (delta.days + 1)  # On ajoute un jour pour éviter la division par 0

        if frequency == 'H':
            format = '%d/%m/%y %M:%H'
            avg /= 24
        elif frequency == 'W':
            avg *= 7
        elif frequency == 'M':
            format = '%B %Y'
            avg *= 30
        elif frequency == 'Q':
            format = '%B %Y'
            avg *= 120
        elif frequency == 'Y':
            format = '%Y'
            avg *= 365

        data.index = data.index.strftime(format)

        labels = data.index.values.tolist()
        data = data.values.tolist()

        # TODO Faire en sorte que tous les dates entre le dernier track et ojd apparaissent
        # Ajoute la date d'aujourd'hui si elle n'y est pas déjà
        # today = timezone.now().strftime(format)
        # if today not in labels:
        #     labels.append(today)
        #     data.append([0])

    return JsonResponse({
        'labels': labels,
        'data': data,
        'avg': round(avg, 2)
    })


def get_other_stats(request):
    if not request.is_ajax():
        return JsonResponse({'error': 'Unauthorized access'}, status=401)

    tracks = get_tracks_from_request(request)

    if not tracks.exists():
        return JsonResponse({})

    hours = {}
    for i in range(24):
        hours[str(i)] = 0

    weekdays = {
        0: 'Lundi',
        1: 'Mardi',
        2: 'Mercredi',
        3: 'Jeudi',
        4: 'Vendredi',
        5: 'Samedi',
        6: 'Dimanche'
    }
    days = {}
    for weekday in weekdays.values():
        days[weekday] = 0

    deltas = []
    prev = None
    for track in tracks:
        dt = make_naive(track.datetime)
        hours[str(dt.hour)] += 1
        days[weekdays[dt.weekday()]] += 1
        if prev:
            # Store the diff between the previous track and this one
            deltas.append(prev.datetime - track.datetime)
        prev = track

    delta_stats = None
    if deltas:
        delta_stats = {
            'deltaMin': str(min(deltas)),
            'deltaAvg': str(sum(deltas, timedelta(0)) / len(deltas)),
            'deltaMax': str(max(deltas))
        }

    return JsonResponse({
        'trackByHourChart': {
            'labels': list(x + 'h' for x in hours.keys()),
            'values': list(hours.values())
        },
        'trackByDayChart': {
            'labels': list(days.keys()),
            'values': list(days.values())
        },
        'deltaStats': delta_stats
    })


@require_POST
def tracker_history(request):
    if not request.is_ajax():
        return JsonResponse({'error': 'Unauthorized access'}, status=401)

    tracks = get_tracks_from_request(request)
    for track in tracks:
        track.form = TrackForm(instance=track)
    html = render_to_string('tracker/include/tbody_tracks.html', {'tracks': tracks}, request)
    return JsonResponse({
        'html': html,
        'trackCount': tracks.count()
    })
