from django.db import models
from django.utils import timezone

from base.models import Profil


class Jeu(models.Model):
    nom = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, null=True)
    createur = models.ForeignKey(Profil, on_delete=models.SET_NULL, null=True, blank=True)
    date_creation = models.DateTimeField(verbose_name="date d'ajout", auto_now_add=True)
    image = models.ImageField(
        help_text="Une image/photo pour identifier le jeu",
        null=True, blank=True, upload_to="jeux/"
    )
    classement = models.BooleanField(default=False, help_text="Cocher cette case pour activer le mode Classement.")

    class Meta:
        verbose_name_plural = 'jeux'

    def __str__(self):
        return self.nom


class Partie(models.Model):
    jeu = models.ForeignKey(Jeu, on_delete=models.CASCADE, related_name='parties')
    date = models.DateTimeField(default=timezone.now)
    joueurs = models.ManyToManyField(Profil, through='PartieJoueur')

    def __str__(self):
        return '%s (%s)' % (self.jeu, self.date)


class PartieJoueur(models.Model):
    partie = models.ForeignKey(Partie, on_delete=models.CASCADE)
    joueur = models.ForeignKey(Profil, on_delete=models.CASCADE)
    score_classement = models.PositiveSmallIntegerField('score ou classement')
