from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Avg
from django.urls import reverse
from django.utils import timezone
from fontawesome_6.fields import IconField

from base.image_utils import optimize_uncommitted_fieldfile


class PhotoOptimizationMixin(models.Model):
    """
    Optimise (resize + WebP) le champ image désigné par `OPTIMIZE_IMAGE_FIELD` à chaque
    sauvegarde d'un nouvel upload. À utiliser sur les modèles dont le champ image n'est
    pas `photo` (sinon voir PhotoAbstract).
    """

    OPTIMIZE_IMAGE_FIELD = None

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        field_name = self.OPTIMIZE_IMAGE_FIELD
        if field_name:
            optimized = optimize_uncommitted_fieldfile(
                getattr(self, field_name, None), field_name
            )
            if optimized is not None:
                setattr(self, field_name, optimized)
        super().save(*args, **kwargs)


class Profil(PhotoOptimizationMixin):
    OPTIMIZE_IMAGE_FIELD = "avatar"

    user = models.OneToOneField(User, on_delete=models.PROTECT, related_name="profil")
    avatar = models.ImageField(null=True, blank=True, upload_to="avatars/")
    birthday = models.DateField("date anniversaire", null=True, blank=True)
    date_creation = models.DateTimeField(
        verbose_name="date de création", auto_now_add=True
    )

    def __str__(self):
        return self.user.username

    def get_absolute_url(self):
        return reverse("base:profil", kwargs={"slug": self.user.username})

    @property
    def note_moyenne(self):
        return self.avis_set.all().aggregate(Avg("note"))["note__avg"]

    @property
    def age(self):
        if not self.birthday:
            return None
        today = timezone.now().date()
        return (
            today.year
            - self.birthday.year
            - ((today.month, today.day) < (self.birthday.month, self.birthday.day))
        )

    @property
    def derniers_avis(self):
        return self.avis_set.order_by("-date_creation").prefetch_related(
            "produit__structure__type"
        )


class Projet(PhotoOptimizationMixin):
    """
    Gestion des projets à afficher sur la page d'accueil
    """

    OPTIMIZE_IMAGE_FIELD = "image"

    nom = models.CharField(max_length=100)
    lien = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Nom de la vue Django vers la page d'accueil du projet",
    )
    image = models.ImageField(null=True, blank=True, upload_to="projet/")
    actif = models.BooleanField(default=True)
    logged_only = models.BooleanField(
        "connecté seulement",
        default=False,
        help_text="Cochez pour afficher ce projet qu'aux personnes connecté sur le site.",
    )
    staff_only = models.BooleanField(
        "staff seulement",
        default=False,
        help_text="Cochez pour afficher ce projet qu'aux personnes faisant partis du staff.",
    )
    external = models.BooleanField(
        "externe",
        default=False,
        help_text="Cochez lorsque le lien pointe vers un site externe à benbb96.com.",
    )
    position = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ("position",)

    def __str__(self):
        return self.nom

    def get_absolute_url(self):
        if self.lien.startswith("http"):
            return self.lien
        return reverse(self.lien)

    def clean(self):
        from config.urls import VIEW_NAMES

        if self.external:
            if not self.lien.startswith("http"):
                raise ValidationError(
                    {
                        "lien": f"{self.lien} n'est pas un lien direct (il doit commencer par http)."
                    }
                )
        elif self.lien not in VIEW_NAMES:
            raise ValidationError(
                {
                    "lien": f"{self.lien} n'est pas un nom de vue correcte (ne pas oublier le namespace)."
                }
            )


class LienReseauSocial(models.Model):
    """
    Gestion des liens vers mes réseaux sociaux
    """

    reseau_social = IconField("réseau social")
    lien = models.URLField()
    ouvrir_nouvel_onglet = models.BooleanField(
        help_text="Indique s'il faut ouvrir le lien dans un nouvel onglet",
        default=False,
    )
    actif = models.BooleanField(default=True)

    class Meta:
        verbose_name = "lien réseau social"
        verbose_name_plural = "liens réseaux sociaux"

    def __str__(self):
        return str(self.reseau_social)


def photo_upload_to(instance, filename):
    """
    Chemin relatif à la racine du storage : <PHOTO_FOLDER>/<YYYY>/<MM>/<DD>/<filename>

    Pas de préfixe 'media/' — il est géré par MEDIA_URL (local) ou GS_LOCATION='media' (GCS).
    """
    folder = getattr(instance.__class__, "PHOTO_FOLDER", "photos")
    from datetime import date

    d = date.today()
    return f"{folder}/{d.year}/{d.month:02d}/{d.day:02d}/{filename}"


class PhotoAbstract(models.Model):
    PHOTO_FOLDER = "photos"

    photo = models.ImageField(
        "photo",
        null=True,
        blank=True,
        upload_to=photo_upload_to,
    )

    class Meta:
        abstract = True

    @property
    def photo_url(self):
        """URL complète de l'image — rétrocompatible avec les anciens chemins Firebase."""
        if not self.photo:
            return ""
        name = self.photo.name or ""
        if not name or name == "placeholder.jpg":
            return ""
        if name.startswith("http"):
            return name
        # Les anciens chemins Firebase contiennent le préfixe 'media/' (ex. 'media/avis/…').
        # Le storage le gère via MEDIA_URL (local) ou GS_LOCATION (GCS) — on ne le stocke pas.
        if name.startswith("media/"):
            name = name[len("media/") :]
        try:
            return self.photo.storage.url(name)
        except Exception:
            return ""

    def save(self, *args, **kwargs):
        optimized = optimize_uncommitted_fieldfile(self.photo, "photo")
        if optimized is not None:
            self.photo = optimized
        super().save(*args, **kwargs)
