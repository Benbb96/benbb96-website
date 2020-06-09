from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Avg
from django.urls import reverse
from django.utils import timezone
from fontawesome.fields import IconField
from pyrebase import pyrebase


class Profil(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT, related_name='profil')
    avatar = models.ImageField(null=True, blank=True, upload_to="avatars/")
    birthday = models.DateField('date anniversaire', null=True, blank=True)
    date_creation = models.DateTimeField(verbose_name="date de création", auto_now_add=True)

    def __str__(self):
        return self.user.username

    def get_absolute_url(self):
        return reverse('base:profil', kwargs={'slug': self.user.username})

    @property
    def note_moyenne(self):
        return self.avis_set.all().aggregate(Avg('note'))['note__avg']

    @property
    def age(self):
        if not self.birthday:
            return None
        today = timezone.now().date()
        return today.year - self.birthday.year - ((today.month, today.day) < (self.birthday.month, self.birthday.day))

    @property
    def derniers_avis(self):
        return self.avis_set.order_by('-date_creation').prefetch_related('produit__structure__type')


class Projet(models.Model):
    """
    Gestion des projets à afficher sur la page d'accueil
    """
    nom = models.CharField(max_length=100)
    lien = models.CharField(
        max_length=100,
        null=True, blank=True,
        help_text="Nom de la vue Django vers la page d'accueil du projet"
    )
    image = models.ImageField(null=True, blank=True, upload_to="projet/")
    actif = models.BooleanField(default=True)
    logged_only = models.BooleanField(
        'connecté seulement', default=False,
        help_text="Cochez pour afficher ce projet qu'aux personnes connecté sur le site."
    )
    staff_only = models.BooleanField(
        'staff seulement', default=False,
        help_text="Cochez pour afficher ce projet qu'aux personnes faisant partis du staff."
    )
    external = models.BooleanField(
        'externe', default=False,
        help_text='Cochez lorsque le lien pointe vers un site externe à benbb96.com.'
    )
    position = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ('position',)

    def __str__(self):
        return self.nom

    def get_absolute_url(self):
        if self.lien.startswith('http'):
            return self.lien
        return reverse(self.lien)

    def clean(self):
        from config.urls import VIEW_NAMES
        if self.external:
            if not self.lien.startswith('http'):
                raise ValidationError(
                    {'lien': "%s n'est pas un lien direct (il doit commencer par http)." % self.lien}
                )
        elif self.lien not in VIEW_NAMES:
            raise ValidationError(
                {'lien': "%s n'est pas un nom de vue correcte (ne pas oublier le namespace)." % self.lien}
            )


class LienReseauSocial(models.Model):
    """
    Gestion des liens vers mes réseaux sociaux
    """
    reseau_social = IconField('réseau social')
    lien = models.URLField()
    ouvrir_nouvel_onglet = models.BooleanField(
        help_text="Indique s'il faut ouvrir le lien dans un nouvel onglet",
        default=False
    )
    actif = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'lien réseau social'
        verbose_name_plural = 'liens réseaux sociaux'

    def __str__(self):
        return str(self.reseau_social)


class PhotoAbstract(models.Model):
    photo = models.TextField(
        'url photo',
        default='placeholder.jpg',
        help_text="Vous pouvez également renseigner l'URL d'une image sur internet."
    )

    class Meta:
        abstract = True

    @property
    def photo_url(self):
        """ Récupère l'URL complète de l'image """
        # Vérifier s'il s'agit d'une URL de photo
        if self.photo.startswith('http'):
            return self.photo
        # Récupération de l'URL grâce à pyrebase
        firebase = pyrebase.initialize_app(settings.FIREBASE_CONFIG)
        storage = firebase.storage()
        return storage.child(self.photo).get_url(None)
