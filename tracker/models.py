from colorfield.fields import ColorField
from django.db import models
from django.urls import reverse
from django.utils import timezone
from fontawesome.fields import IconField

from base.models import Profil


class Tracker(models.Model):
    createur = models.ForeignKey(Profil, related_name='trackers', on_delete=models.CASCADE)
    nom = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, null=True)
    icone = IconField()
    color = ColorField(default='#FFFFFF')
    date_creation = models.DateTimeField(verbose_name="date de création", auto_now_add=True)

    def __str__(self):
        return self.nom

    def get_absolute_url(self):
        return reverse('tracker:detail-tracker', kwargs={'slug': self.slug})


class Track(models.Model):
    tracker = models.ForeignKey(Tracker, related_name='tracks', on_delete=models.CASCADE)
    datetime = models.DateTimeField('date et heure', default=timezone.now)
    commentaire = models.CharField(max_length=255, help_text='Un texte pour donner une explication sur ce track.',
                                   blank=True)

    class Meta:
        ordering = ('-datetime',)

    def __str__(self):
        return str(self.tracker) + ' (' + self.datetime.strftime('%d/%m/%y %H:%M') + ')'
