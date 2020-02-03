from colorfield.fields import ColorField
from django.contrib.auth.models import Group
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Q
from django.urls import reverse
from fontawesome.fields import IconField
from geoposition.fields import GeopositionField

from base.models import Profil, PhotoAbstract


class SpotTag(models.Model):
    nom = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, null=True)
    date_creation = models.DateTimeField('date de création', auto_now_add=True)
    icone = IconField('icône', blank=True)
    color = ColorField('couleur', default='#FFFFFF')

    class Meta:
        ordering = ('nom',)

    def __str__(self):
        return self.nom

    def get_absolute_url(self):
        return reverse('my_spot:tag', kwargs={'tag_slug': self.slug})


PUBLIC = 1
PARTAGE = 2
CACHE = 3
VISIBILITE = (
    (PUBLIC, 'Public'),
    (PARTAGE, 'Partagé'),
    (CACHE, 'Caché'),
)


class SpotManager(models.Manager):
    def get_queryset(self):
        return super(SpotManager, self).get_queryset()\
            .select_related('explorateur__user').prefetch_related('photos', 'notes')\
            .annotate(moyenne=models.Avg('notes'), note_count=models.Count('notes', distinct=True))

    def visible_for_user(self, user):
        if not user.is_authenticated:
            # Seulement les publics pour un utilisateur non connecté
            return self.get_queryset().filter(visibilite=PUBLIC)
        # Les publics + ceux qu'il a créé et ceux de ses groupes
        return self.get_queryset().filter(
            Q(visibilite=PUBLIC) | Q(explorateur=user.profil) | Q(groupes__in=user.groups.all())
        )


class Spot(models.Model):
    nom = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, null=True)
    description = models.TextField(blank=True)
    position = GeopositionField()
    explorateur = models.ForeignKey(
        Profil,
        related_name='spots',
        help_text='Personne ayant exploré le spot',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    visibilite = models.PositiveSmallIntegerField(
        'visibilité',
        choices=VISIBILITE,
        default=CACHE,
        help_text="Visbilité du spot : Public = visible par tous ; Privé = visible par les membre du groupe ; "
                  "Caché = seul le possésseur peut le voir."
    )
    groupes = models.ManyToManyField(Group, verbose_name='partagé aux groupes', related_name='spots', blank=True)
    tags = models.ManyToManyField(SpotTag, related_name='spots', blank=True)
    date_creation = models.DateTimeField('date de création', auto_now_add=True)
    date_modification = models.DateTimeField('dernière modification', auto_now=True)

    objects = SpotManager()

    class Meta:
        ordering = ('-date_creation',)

    def __str__(self):
        return self.nom

    def get_absolute_url(self):
        return reverse('my_spot:spot_detail', kwargs={'spot_slug': self.slug})


class SpotPhoto(PhotoAbstract):
    spot = models.ForeignKey(Spot, on_delete=models.CASCADE, related_name='photos')
    photographe = models.ForeignKey(Profil, on_delete=models.CASCADE, related_name='spot_photos')
    description = models.CharField(max_length=240, blank=True)
    date_ajout = models.DateTimeField("date d'ajout", auto_now_add=True)

    class Meta:
        ordering = ('date_ajout',)

    def __str__(self):
        return 'Photo de {0} sur le spot "{1}"'.format(self.photographe, self.spot)


class SpotNote(models.Model):
    spot = models.ForeignKey(Spot, on_delete=models.CASCADE, related_name='notes')
    auteur = models.ForeignKey(Profil, on_delete=models.CASCADE, related_name='spot_notes')
    note = models.PositiveSmallIntegerField(
        default=5,
        help_text='Une note entre 0 et 10',
        validators=[MinValueValidator(0), MaxValueValidator(10)]
    )
    justification = models.TextField(blank=True)
    date_ajout = models.DateTimeField("date d'ajout", auto_now_add=True)

    class Meta:
        ordering = ('-date_ajout',)

    def __str__(self):
        return 'Note de {0} sur le spot "{1}" : {2}/10'.format(self.auteur, self.spot, self.note)
