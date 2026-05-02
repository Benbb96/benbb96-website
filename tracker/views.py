import string
from datetime import datetime, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.html import format_html
from django.utils.timezone import make_aware, make_naive
from django.views.decorators.http import require_POST
from django.views.generic import UpdateView, DeleteView
from django_pandas.io import read_frame
import pandas as pd
from rest_framework import generics, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from tracker.forms import TrackForm, TrackerForm, SelectTrackersForm
from tracker.models import Tracker, Track
from tracker.serializers import TrackerSerializer, CustomTrackSerializer, TrackSerializer


class TrackerView(ModelViewSet):
    queryset = Tracker.objects.all()
    serializer_class = TrackerSerializer

    def get_queryset(self):
        return self.request.user.profil.trackers.all()

    def perform_create(self, serializer):
        serializer.save(createur=self.request.user.profil)

    @action(detail=False, methods=['patch'])
    def reorder(self, request):
        ids = request.data.get('ids', [])
        trackers = self.get_queryset()
        if set(ids) != {t.id for t in trackers}:
            return Response({'error': 'Liste d\'IDs incomplète ou invalide'}, status=status.HTTP_400_BAD_REQUEST)
        tracker_map = {t.id: t for t in trackers}
        to_update = []
        for order, tracker_id in enumerate(ids):
            tracker = tracker_map[tracker_id]
            tracker.order = order
            to_update.append(tracker)
        Tracker.objects.bulk_update(to_update, ['order'])
        return Response({'status': 'ok'})


class TrackView(ModelViewSet):
    queryset = Track.objects.all()
    serializer_class = TrackSerializer

    def get_queryset(self):
        return super().get_queryset().filter(tracker__createur__user=self.request.user)


@login_required
def tracker_list(request):
    trackers = Tracker.objects.filter(createur=request.user.profil)

    form = TrackerForm(request.POST or None)
    if form.is_valid():
        if trackers.filter(nom=form.cleaned_data['nom']).exists():
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

    def get_queryset(self):
        return self.request.user.profil.trackers.all()


class TrackerDeleteView(DeleteView):
    model = Tracker
    success_url = reverse_lazy('tracker:liste-tracker')

    def get_queryset(self):
        return self.request.user.profil.trackers.all()


@login_required
def tracker_quick_add(request, pk):
    tracker = get_object_or_404(Tracker.objects.filter(createur=request.user.profil), id=pk)
    if tracker.type == Tracker.TYPE_MESURE:
        messages.info(request, 'Ce tracker nécessite une valeur, veuillez l\'ajouter depuis la page de détail.')
        return redirect(tracker)
    Track.objects.create(tracker=tracker)
    messages.success(request, 'Un track a bien été ajouté sur le tracker %s' % tracker)
    return redirect('tracker:liste-tracker')


@login_required
def tracker_detail(request, pk):
    tracker = get_object_or_404(Tracker.objects.filter(createur=request.user.profil), id=pk)

    form = TrackForm(request.POST or None, initial={'datetime': timezone.now()}, tracker_type=tracker.type)
    if form.is_valid():
        track = form.save(commit=False)
        track.tracker = tracker
        track.save()
        return redirect(tracker)

    tracks = tracker.tracks.all()
    for track in tracks:
        track.form = TrackForm(instance=track, tracker_type=tracker.type)

    return render(request, 'tracker/tracker_detail.html', {
        'tracker': tracker,
        'tracks': tracks,
        'form': form
    })


class TrackUpdateView(generics.UpdateAPIView):
    queryset = Track.objects.all()
    serializer_class = CustomTrackSerializer


class TrackDeleteView(generics.DestroyAPIView):
    queryset = Track.objects.all()
    serializer_class = CustomTrackSerializer


def get_tracks_from_request(request):
    ids = request.POST.getlist('id[]')
    trackers = {}
    for tracker_id in ids:
        tracker = get_object_or_404(Tracker.objects.filter(createur=request.user.profil), id=tracker_id)
        trackers[tracker] = tracker.tracks.all()

    start = request.POST.get('start', None)
    end = request.POST.get('end', None)

    if start:
        start = make_aware(datetime.strptime(start, '%y-%m-%d %H:%M:%S'))
        for tracker, tracks in trackers.items():
            trackers[tracker] = tracks.filter(datetime__gte=start)
    if end:
        end = make_aware(datetime.strptime(end, '%y-%m-%d %H:%M:%S'))
        for tracker, tracks in trackers.items():
            trackers[tracker] = tracks.filter(datetime__lte=end)

    return trackers


@require_POST
def tracker_data(request):
    if not request.is_ajax():
        return JsonResponse({'error': 'Unauthorized access'}, status=401)

    trackers = get_tracks_from_request(request)
    frequency = request.POST.get('frequency', 'D')

    date_format = '%d/%m/%y'
    if frequency == 'h':
        date_format = '%d/%m/%y %H:%M'
    elif frequency in ('ME', 'QE'):
        date_format = '%B %Y'
    elif frequency == 'YE':
        date_format = '%Y'

    datasets = []
    labels = {}
    averages = []

    for tracker, tracks in trackers.items():
        if not tracks.exists():
            continue

        if tracker.type == Tracker.TYPE_MESURE:
            df = read_frame(tracks, fieldnames=['datetime', 'valeur'])
            df.loc[:, 'datetime'] = pd.to_datetime(df['datetime']).dt.tz_convert('Europe/Paris')
            df.index = df['datetime']
            df = df.drop(columns=['datetime']).dropna()

            if df.empty:
                continue

            data_mean = df.resample(frequency)['valeur'].mean()
            data_min = df.resample(frequency)['valeur'].min()
            data_max = df.resample(frequency)['valeur'].max()

            averages.append({
                'tracker': tracker.nom,
                'avg': round(float(df['valeur'].mean()), 2),
                'min': float(df['valeur'].min()),
                'max': float(df['valeur'].max()),
                'isValeur': True,
            })

            data_mean.index = data_mean.index.strftime(date_format)
            data_min.index = data_min.index.strftime(date_format)
            data_max.index = data_max.index.strftime(date_format)

            for i, label in enumerate(data_mean.index.tolist()):
                label_date = datetime.strptime(label, date_format)
                val = {
                    'mean': None if pd.isna(data_mean.iloc[i]) else round(float(data_mean.iloc[i]), 2),
                    'min': None if pd.isna(data_min.iloc[i]) else float(data_min.iloc[i]),
                    'max': None if pd.isna(data_max.iloc[i]) else float(data_max.iloc[i]),
                }
                if label_date not in labels:
                    labels[label_date] = {tracker.nom: val}
                else:
                    labels[label_date][tracker.nom] = val

            datasets.append({
                'label': tracker.nom,
                'backgroundColor': tracker.rgba_background_color,
                'trackerType': Tracker.TYPE_MESURE,
            })

        else:
            df = read_frame(tracks, fieldnames=['datetime'])
            df.loc[:, 'datetime'] = pd.to_datetime(df['datetime']).dt.tz_convert('Europe/Paris')
            df.index = df['datetime']
            df.loc[:, 'count'] = 1
            data = df.drop(columns=['datetime']).resample(frequency).sum()

            delta = tracks.latest('datetime').datetime.date() - tracks.earliest('datetime').datetime.date()
            avg = tracks.count() / (delta.days + 1)

            if frequency == 'h':
                avg /= 24
            elif frequency == 'W':
                avg *= 7
            elif frequency == 'ME':
                avg *= 30
            elif frequency == 'QE':
                avg *= 120
            elif frequency == 'YE':
                avg *= 365

            averages.append({'tracker': tracker.nom, 'avg': round(avg, 2), 'isValeur': False})

            data.index = data.index.strftime(date_format)
            data_values = data.values.tolist()

            for i, label in enumerate(data.index.tolist()):
                label_date = datetime.strptime(label, date_format)
                val = {'count': data_values[i][0]}
                if label_date not in labels:
                    labels[label_date] = {tracker.nom: val}
                else:
                    labels[label_date][tracker.nom] = val

            datasets.append({
                'label': tracker.nom,
                'backgroundColor': tracker.rgba_background_color,
                'trackerType': Tracker.TYPE_EVENEMENT,
            })

    sorted_labels = sorted(labels.keys())

    for dataset in datasets:
        if dataset['trackerType'] == Tracker.TYPE_MESURE:
            dataset['data'] = [labels[label].get(dataset['label'], {}).get('mean') for label in sorted_labels]
            dataset['minData'] = [labels[label].get(dataset['label'], {}).get('min') for label in sorted_labels]
            dataset['maxData'] = [labels[label].get(dataset['label'], {}).get('max') for label in sorted_labels]
        else:
            dataset['data'] = [labels[label].get(dataset['label'], {}).get('count', 0) for label in sorted_labels]

    return JsonResponse({
        'labels': [label.strftime(date_format) for label in sorted_labels],
        'datasets': datasets,
        'averages': averages,
    })


def format_timedelta(td):
    """
    Formate correctement un écart de temps avec les jours, heures, minutes et secondes

    :param timedelta td: le timedelta à formater
    :return: la chaîne de caractère formatée
    :rtype: str
    """
    seconds = td.total_seconds()
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    if days > 0:
        return '%d jour%s %dh %dm %ds' % (days, ('s' if days > 1 else ''), hours, minutes, seconds)
    elif hours > 0:
        return '%dh %dm %ds' % (hours, minutes, seconds)
    elif minutes > 0:
        return '%dm %ds' % (minutes, seconds)
    else:
        return '%ds' % seconds


def get_other_stats(request):
    if not request.is_ajax():
        return JsonResponse({'error': 'Unauthorized access'}, status=401)

    trackers = get_tracks_from_request(request)
    if not len(trackers) == 1:
        return JsonResponse({})

    tracker_obj = next(iter(trackers))
    tracks = trackers[tracker_obj]
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

    words = {}
    deltas = []
    prev = minimum = maximum = None
    min_1 = min_2 = max_1 = max_2 = None
    for track in tracks:
        # Compte les mots présents dans chaque track pour en faire un nuage de mots-clefs
        if track.commentaire:
            # Récupère tous les mots séparés par des espaces
            commentaire_words = track.commentaire.split()
            # Prépare une table de traduction pour retirer la ponctuation
            table = str.maketrans('', '', string.punctuation)
            # J'en profite aussi pour mettre tous les mots en miniscule
            stripped = [w.translate(table).lower() for w in commentaire_words]
            for word in stripped:
                # Incrémente le compteur pour le mot en question
                if word not in words.keys():
                    words[word] = 1
                else:
                    words[word] += 1

        # Récupère la datetime du track et incrémente les compteurs de l'heure et de jour de la semaine
        dt = make_naive(track.datetime)
        hours[str(dt.hour)] += 1
        days[weekdays[dt.weekday()]] += 1
        if prev:
            # Sauvegarde la différence entre le datetime précédent et l'actuel
            delta = prev.datetime - track.datetime
            deltas.append(delta)
            # Garde le minimum et le maximum avec le datetime correspondant
            if not minimum or delta < minimum:
                minimum = delta
                min_1 = timezone.localtime(track.datetime)
                min_2 = timezone.localtime(prev.datetime)
            if not maximum or delta > maximum:
                maximum = delta
                max_1 = timezone.localtime(track.datetime)
                max_2 = timezone.localtime(prev.datetime)
        prev = track

    delta_stats = None
    if deltas and min_1 and min_2 and max_1 and max_2:
        date_format = '%d/%m/%y %H:%M'
        delta_stats = {
            'deltaMin': format_html(
                '<b>{}</b> <br><small>Entre le {} et le {}</small>',
                format_timedelta(minimum), min_1.strftime(date_format), min_2.strftime(date_format)
            ),
            'deltaAvg': format_timedelta(sum(deltas, timedelta(0)) / len(deltas)),
            'deltaMax': format_html(
                '<b>{}</b> <br><small>Entre le {} et le {}</small>',
                format_timedelta(maximum), max_1.strftime(date_format), max_2.strftime(date_format)
            )
        }

    valeur_stats = None
    if tracker_obj.type == Tracker.TYPE_MESURE:
        valeurs = [t.valeur for t in tracks if t.valeur is not None]
        if valeurs:
            valeur_stats = {
                'min': min(valeurs),
                'max': max(valeurs),
                'avg': round(sum(valeurs) / len(valeurs), 2),
                'count': len(valeurs),
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
        'deltaStats': delta_stats,
        'valeurStats': valeur_stats,
        'words': {k: v for k, v in sorted(words.items(), key=lambda item: item[1], reverse=True)[:50]}
    })


@require_POST
def tracker_history(request):
    if not request.is_ajax():
        return JsonResponse({'error': 'Unauthorized access'}, status=401)

    trackers = get_tracks_from_request(request)
    total_count = 0
    all_tracks = []
    show_valeur = any(t.type == Tracker.TYPE_MESURE for t in trackers.keys())

    for tracker, tracks in trackers.items():
        for track in tracks:
            track.form = TrackForm(instance=track, tracker_type=tracker.type)
        if len(trackers) == 1:
            return JsonResponse({
                'html': render_to_string(
                    'tracker/include/tbody_tracks.html',
                    {'tracks': tracks, 'show_valeur': show_valeur},
                    request
                ),
                'trackCount': tracks.count()
            })
        else:
            all_tracks += list(tracks)
            total_count += tracks.count()
    return JsonResponse({
        'html': render_to_string(
            'tracker/include/tbody_tracks.html',
            {'tracks': sorted(all_tracks, key=lambda item: item.datetime, reverse=True), 'compare': True, 'show_valeur': show_valeur},
            request
        ),
        'trackCount': total_count
    })


@login_required
def compare_trackers(request):
    form = SelectTrackersForm(data=request.GET or None, user=request.user)
    trackers = []
    first_track = last_track = None
    if form.is_valid():
        trackers = form.cleaned_data.get('trackers', [])
        all_tracks = Track.objects.filter(tracker__in=trackers)
        first_track = all_tracks.earliest('datetime')
        last_track = all_tracks.latest('datetime')
    return render(request, 'tracker/compare_trackers.html', {
        'form': form,
        'trackers': trackers,
        'first_track': first_track,
        'last_track': last_track,
        'has_mesure': any(t.type == Tracker.TYPE_MESURE for t in trackers),
    })
