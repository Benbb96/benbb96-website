from colorfield.fields import ColorField
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify

from base.models import Profil, PhotoAbstract


class Logement(models.Model):
    nom = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    date_creation = models.DateTimeField('date de création', auto_now_add=True)
    habitants = models.ManyToManyField(Profil, related_name='logements')

    class Meta:
        ordering = ('nom',)

    def __str__(self):
        return self.nom

    def save(self, *args, **kwargs):
        # Ajout du slug s'il n'a pas été fourni
        if not self.slug:
            slug = slugify(self.nom)
            # Vérification si ce slug existe déjà
            if Logement.objects.filter(slug=slug).exists():
                counter = 2
                slug_proposition = f'{slug}-{counter}'
                while Logement.objects.filter(slug=slug_proposition).exists():
                    counter += 1
                    slug_proposition = f'{slug}-{counter}'
                slug = slug_proposition
            # Sauvegarde su slug unique
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('super-moite-moite:detail-logement', kwargs={'slug': self.slug})

    def points_par_profil(self, profil):
        if profil not in self.habitants.all():
            raise ValueError(f"{profil} n'est pas un habitant du logement")

        # Calcul de la somme de point pour ce profil sur ce logement
        total = 0
        for track in profil.tracktache_set.filter(tache__categorie__logement=self):
            try:
                total += track.tache.pointtache_set.get(profil=profil).point
            except PointTache.DoesNotExist:
                # Default is 1 point
                total += 1
        return total


class Categorie(models.Model):
    nom = models.CharField(max_length=100)
    logement = models.ForeignKey(Logement, on_delete=models.CASCADE, related_name='categories')
    order = models.PositiveIntegerField(default=0, editable=False, db_index=True)
    couleur = ColorField(default='#FFFFFF')

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.nom


class Tache(PhotoAbstract):
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    categorie = models.ForeignKey(Categorie, on_delete=models.CASCADE, related_name='taches')
    order = models.PositiveIntegerField(default=0, editable=False, db_index=True)

    def __str__(self):
        return self.nom

    class Meta:
        ordering = ['order']


class PointTache(models.Model):
    point = models.PositiveSmallIntegerField(default=1)
    tache = models.ForeignKey(Tache, on_delete=models.CASCADE, related_name='point_profils')
    profil = models.ForeignKey(Profil, on_delete=models.CASCADE, related_name='point_taches')

    class Meta:
        unique_together = ('tache', 'profil')


class TrackTache(models.Model):
    profil = models.ForeignKey(Profil, on_delete=models.CASCADE, related_name='tache_tracks')
    tache = models.ForeignKey(Tache, on_delete=models.CASCADE, related_name='tracks')
    datetime = models.DateTimeField('date et heure', default=timezone.now)
    commentaire = models.CharField(
        max_length=255, help_text='Un texte pour donner une explication sur ce track.', blank=True
    )

    class Meta:
        ordering = ('-datetime',)


