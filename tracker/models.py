from colorfield.fields import ColorField
from django.db import models
from fontawesome.fields import IconField

from base.models import Profil


class Tracker(models.Model):
    createur = models.ForeignKey(Profil, related_name='trackers', on_delete=models.CASCADE)
    nom = models.CharField(max_length=100)
    icone = IconField()
    color = ColorField(default='#FFFFFF')
    date_creation = models.DateTimeField(verbose_name="date de création", auto_now_add=True)

    def __str__(self):
        return self.nom


class Track(models.Model):
    tracker = models.ForeignKey(Tracker, related_name='tracks', on_delete=models.CASCADE)
    datetime = models.DateTimeField('date et heure', auto_now_add=True)
    commentaire = models.CharField(max_length=255, help_text='Un texte pour donner une explication sur ce track.')

    def __str__(self):
        return str(self.tracker) + ' - ' + str(self.datetime)
