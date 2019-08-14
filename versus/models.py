from django.db import models
from django.urls import reverse
from django.utils import timezone

from base.models import Profil


class Joueur(models.Model):
    nom = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, null=True)
    profil = models.ForeignKey(Profil, on_delete=models.SET_NULL, null=True, blank=True)
    date_creation = models.DateTimeField(verbose_name="date d'ajout", auto_now_add=True)

    def __str__(self):
        return self.nom

    def get_absolute_url(self):
        return reverse('versus:detail-joueur', kwargs={'slug': self.slug})

    @property
    def nb_victoire(self):
        nb = 0
        for partiejoueur in self.partiejoueur_set.all():
            if self in partiejoueur.partie.get_winners():
                nb += 1
        return nb

    @property
    def ratio(self):
        return round(self.nb_victoire / self.partiejoueur_set.count() * 100)


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

    def get_absolute_url(self):
        return reverse('versus:detail-jeu', kwargs={'slug': self.slug})


class Partie(models.Model):
    jeu = models.ForeignKey(Jeu, on_delete=models.CASCADE, related_name='parties')
    date = models.DateTimeField(default=timezone.now)
    joueurs = models.ManyToManyField(Joueur, through='PartieJoueur')

    class Meta:
        ordering = ('-date',)

    def __str__(self):
        return '%s (%s)' % (self.jeu, self.date)

    def get_winners(self):
        """ Retourne le ou les gagnants de cette partie """
        if self.jeu.classement:
            # On veut la ou les personnes arrivées en première place
            return Joueur.objects.filter(partiejoueur__partie=self, partiejoueur__score_classement=1)
        else:
            # On cherche d'abord le score maximum
            maximum = max(partiejoueur.score_classement for partiejoueur in self.partiejoueur_set.all())
            # Puis on retourne tous les joueurs ayant ce score
            return Joueur.objects.filter(partiejoueur__partie=self, partiejoueur__score_classement=maximum)


class PartieJoueur(models.Model):
    partie = models.ForeignKey(Partie, on_delete=models.CASCADE)
    joueur = models.ForeignKey(Joueur, on_delete=models.CASCADE)
    score_classement = models.PositiveSmallIntegerField('score ou classement')

    class Meta:
        unique_together = (('partie', 'joueur'),)
