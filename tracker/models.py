from adminsortable.models import SortableMixin, SortableForeignKey
from colorfield.fields import ColorField
from django.db import models
from django.urls import reverse
from django.utils import timezone
from fontawesome.fields import IconField

from base.models import Profil


class Tracker(SortableMixin):
    createur = SortableForeignKey(Profil, verbose_name='créateur', related_name='trackers', on_delete=models.CASCADE)
    nom = models.CharField(max_length=100)
    icone = IconField('icône')
    color = ColorField('couleur', default='#FFFFFF')
    date_creation = models.DateTimeField('date de création', auto_now_add=True)
    order = models.PositiveIntegerField(default=0, editable=False, db_index=True)

    class Meta:
        unique_together = (('createur', 'nom'),)
        ordering = ['order']

    def __str__(self):
        return self.nom

    def get_absolute_url(self):
        return reverse('tracker:detail-tracker', kwargs={'pk': self.id})

    def track_by_hour(self):
        hours = {}
        for i in range(24):
            hours[str(i)] = 0

        for track in self.tracks.all():
            hours[str(track.datetime.hour)] += 1

        return hours

    def track_by_day(self):
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

        for track in self.tracks.all():
            days[weekdays[track.datetime.weekday()]] += 1

        return days

    @property
    def rgba_background_color(self):
        """
        Retourne la commande css pour afficher la couleur du tracker avec une opacité diminué afin de voir
        les différentes courbes les unes à travers les autres.
        """
        opacity = '0.3'
        return 'rgba(%s,%s)' % (
            ','.join(tuple(str(int(self.color.lstrip('#')[i:i+2], 16)) for i in (0, 2, 4))),
            opacity
        )


class TrackManager(models.Manager):
    def first_track(self):
        return self.get_queryset().earliest('datetime')

    def last_track(self):
        return self.get_queryset().latest('datetime')


class Track(models.Model):
    tracker = models.ForeignKey(Tracker, related_name='tracks', on_delete=models.CASCADE)
    datetime = models.DateTimeField('date et heure', default=timezone.now)
    commentaire = models.CharField(
        max_length=255, help_text='Un texte pour donner une explication sur ce track.', blank=True
    )

    objects = TrackManager()

    class Meta:
        ordering = ('-datetime',)

    def __str__(self):
        return str(self.tracker) + ' (' + self.datetime.strftime('%d/%m/%y %H:%M') + ')'
