from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.db import models
from django.urls import reverse
from django.utils.text import slugify

from base.models import Profil, PhotoAbstract
from geoposition.fields import GeopositionField


telephone_validator = RegexValidator('^(0|\\+33|0033)[1-9][0-9]{8}$', "Ce numéro n'est pas valide.")


def apercu(text):
    """
    Retourne les 80 premiers caractères du texte donné en paramètre.
    S'il  y a plus de 80 caractères, il faut rajouter des points de suspension.
    """
    apercu = text[0:80]
    if len(text) > 80:
        return '%s...' % apercu
    return apercu


class CategorieProduit(models.Model):
    nom = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = 'catégorie de produit'
        verbose_name_plural = 'catégories de produit'
        ordering = ('nom',)

    def __str__(self):
        return self.nom

    def get_absolute_url(self):
        return reverse('avis:categorie', kwargs={'slug': self.slug})


class TypeStructure(models.Model):
    nom = models.CharField(max_length=100)
    categories = models.ManyToManyField(
        CategorieProduit, help_text='Selectionnez la ou les catégories de produit possibles pour ce type de structure.'
    )

    class Meta:
        verbose_name = "type de structure"
        verbose_name_plural = "types de structure"

    def __str__(self):
        return self.nom


class StructureManager(models.Manager):
    def get_queryset(self):
        return super(StructureManager, self).get_queryset()\
            .select_related('type').prefetch_related('produit_set')\
            .annotate(moyenne=models.Avg('produit__avis__note'), produit_count=models.Count('produit', distinct=True))


class Structure(models.Model):
    nom = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    type = models.ForeignKey(TypeStructure, on_delete=models.PROTECT, verbose_name='type de la structure')
    informations = models.TextField(blank=True, help_text='Informations utiles et relatives à la structure.')
    lien = models.URLField(max_length=255, blank=True, help_text='Le lien vers le site internet.')
    telephone = models.CharField(
        max_length=20, blank=True, help_text='Indicatif facultatif et sans espaces.', validators=[telephone_validator]
    )
    adresse = GeopositionField(blank=True)
    date_creation = models.DateTimeField(verbose_name="date d'ajout", auto_now_add=True)

    objects = StructureManager()

    class Meta:
        ordering = ('nom',)

    def __str__(self):
        return "%s - %s" % (self.type, self.nom)

    def get_absolute_url(self):
        return reverse('avis:structure', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nom)
        super(Structure, self).save(*args, **kwargs)

    def apercu_informations(self):
        return apercu(self.informations)
    apercu_informations.short_description = 'Aperçu des informations'
    apercu_informations.admin_order_field = 'description'


class ProduitManager(models.Manager):
    def get_queryset(self):
        return super(ProduitManager, self).get_queryset()\
            .select_related('structure__type').prefetch_related('avis_set')\
            .annotate(moyenne=models.Avg('avis__note'), avis_count=models.Count('avis', distinct=True))


class Produit(models.Model):
    structure = models.ForeignKey(Structure, on_delete=models.PROTECT)
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True, help_text='Une description du produit.')
    prix = models.DecimalField(max_digits=4, decimal_places=2)
    date_creation = models.DateTimeField(verbose_name="date d'ajout", auto_now_add=True)
    categories = models.ManyToManyField(
        CategorieProduit, help_text='Sélectionnez la ou les catégories de ce produit.', blank=True
    )

    objects = ProduitManager()

    class Meta:
        ordering = ('nom',)

    def __str__(self):
        return '%s [%s]' % (self.nom, self.structure)

    def get_absolute_url(self):
        return reverse('avis:produit', kwargs={'pk': self.pk})

    def apercu_description(self):
        return apercu(self.description)
    apercu_description.short_description = 'Description'
    apercu_description.admin_order_field = 'description'


class Avis(PhotoAbstract):
    produit = models.ForeignKey(Produit, on_delete=models.PROTECT)
    auteur = models.ForeignKey(Profil, on_delete=models.PROTECT)
    avis = models.TextField(blank=True, help_text='Ton avis en quelques mots sur le produit.')
    note = models.PositiveIntegerField(default=5, help_text='Une note entre 0 et 10',
                                       validators=[MinValueValidator(0), MaxValueValidator(10)])
    photo = models.TextField(null=True, blank=True)
    prive = models.BooleanField('privé', default=False,
                                help_text='Cochez pour cacher cet avis aux utilisateurs non connectés')
    date_creation = models.DateTimeField(verbose_name="date d'ajout", auto_now_add=True)
    date_edition = models.DateTimeField(verbose_name="date de dernière modification", auto_now=True)

    class Meta:
        verbose_name_plural = 'avis'
        ordering = ('-date_edition',)

    def __str__(self):
        return '%s : %s (%d/10)' % (self.auteur, self.produit.nom, self.note)

    def get_absolute_url(self):
        return reverse('avis:detail-avis', kwargs={'pk': self.pk})

    def apercu_avis(self):
        return apercu(self.avis)
    apercu_avis.short_description = "Aperçu de l'avis"

    def has_been_edited(self):
        """ Compare les dates de création et d'édition pour savoir si l'objet a été édité """
        return self.date_creation.replace(microsecond=0) != self.date_edition.replace(microsecond=0)
