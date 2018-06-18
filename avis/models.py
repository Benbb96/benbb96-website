from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.db import models
from django.contrib.auth.models import User
from django.db.models import Avg
from django.urls import reverse
from geoposition.fields import GeopositionField


class Profil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # La liaison OneToOne vers le modèle User
    avatar = models.ImageField(null=True, blank=True, upload_to="media/avatars/")
    date_creation = models.DateTimeField(verbose_name="date de création", auto_now_add=True)

    def __str__(self):
        return self.user.username

    @property
    def note_moyenne(self):
        return self.avis_set.all().aggregate(Avg('note'))['note__avg']


telephone_validator = RegexValidator('^(0|\\+33|0033)[1-9][0-9]{8}$', "Ce numéro n'est pas valide.")


class Restaurant(models.Model):
    nom = models.CharField(max_length=100)
    informations = models.TextField(blank=True, help_text='Informations utiles et relatives au restaurant')
    lien = models.URLField(max_length=255, blank=True, help_text='Le lien vers le site internet')
    telephone = models.CharField(max_length=20, blank=True, help_text='Indicatif facultatif et sans espaces.', validators=[telephone_validator])
    adresse = GeopositionField(null=True, blank=True)
    date_creation = models.DateTimeField(verbose_name="date d'ajout", auto_now_add=True)

    def __str__(self):
        return self.nom

    @property
    def note_moyenne(self):
        moyenne = 0
        count = 0
        for plat in self.plat_set.all():
            if plat.avis_set.count():
                moyenne += plat.avis_set.all().aggregate(Avg('note'))['note__avg']
                count += 1
        if count:
            moyenne = moyenne / count
        return moyenne


class Plat(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.PROTECT)
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True, help_text='Une description du plat')
    prix = models.DecimalField(max_digits=4, decimal_places=2)
    date_creation = models.DateTimeField(verbose_name="date d'ajout", auto_now_add=True)

    def __str__(self):
        return self.nom

    @property
    def note_moyenne(self):
        return self.avis_set.all().aggregate(Avg('note'))['note__avg']


class Avis(models.Model):
    class Meta:
        verbose_name_plural = 'avis'

    plat = models.ForeignKey(Plat, on_delete=models.PROTECT)
    auteur = models.ForeignKey(Profil, on_delete=models.PROTECT)
    avis = models.TextField(blank=True, help_text='Ton avis en quelques mots sur le plat')
    note = models.PositiveIntegerField(default=5, help_text='Une note entre 0 et 10',
                                       validators=[MinValueValidator(0), MaxValueValidator(10)])
    photo = models.ImageField(null=True, blank=True, upload_to="media/avis/")
    date_creation = models.DateTimeField(verbose_name="date d'ajout", auto_now_add=True)
    date_edition = models.DateTimeField(verbose_name="date de dernière modification", auto_now=True)

    def __str__(self):
        return str(self.auteur) + ' : ' + self.plat.nom + ' (' + str(self.note) + '/10)'

    def get_absolute_url(self):
        return reverse('avis:detail-avis', kwargs={'pk': self.pk})
