from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.utils.text import slugify
from django.views.decorators.http import require_POST
from django_pandas.io import read_frame
import pandas as pd

from tracker.forms import TrackForm, TrackerForm
from tracker.models import Tracker


@login_required
def tracker_list(request):
    trackers = Tracker.objects.filter(createur=request.user.profil)

    form = TrackerForm(request.POST or None)
    if form.is_valid():
        tracker = form.save(commit=False)
        tracker.createur = request.user.profil
        tracker.slug = slugify(tracker.nom)
        tracker.save()

        return redirect('tracker:liste-tracker')

    return render(request, 'tracker/tracker_list.html', {'trackers': trackers, 'form': form})


@login_required
def tracker_detail(request, slug):
    tracker = get_object_or_404(Tracker.objects.filter(createur=request.user.profil), slug=slug)

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


@require_POST
def tracker_data(request):
    if not request.is_ajax():
        return JsonResponse({'error':'Unauthorized access'}, status_code=401)

    tracker = get_object_or_404(Tracker.objects.filter(createur=request.user.profil), id=request.POST.get('id'))

    # Regroupe les données par date pour faire des stats
    frequency = request.POST.get('frequency', 'D')
    df = read_frame(tracker.tracks.all(), fieldnames=['datetime'])
    df['datetime'] = pd.to_datetime(df['datetime'])
    df['datetime'] = df['datetime'].dt.tz_convert('Europe/Paris')
    df.index = df['datetime']
    df['count'] = [1] * tracker.tracks.count()
    data = df.resample(frequency).sum()

    delta = timezone.now().date() - tracker.tracks.earliest('datetime').datetime.date()

    format = '%d/%m/%y'
    avg = tracker.tracks.count() / (delta.days + 1)  # On ajoute un jour pour éviter la division par 0

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
    data= data.values.tolist()

    return JsonResponse({
        'labels': labels,
        'data': data,
        'avg': round(avg, 2)
    })

