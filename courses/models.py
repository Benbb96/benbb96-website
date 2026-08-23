import uuid

from autoslug import AutoSlugField
from colorfield.fields import ColorField
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone
from fontawesome_6.fields import IconField

from base.models import Profil


def _quantite_field(**kwargs):
    """DecimalField à 3 décimales — cf. conception.md §11 (import de ticket : « 0,834 kg »)."""
    kwargs.setdefault("max_digits", 9)
    kwargs.setdefault("decimal_places", 3)
    kwargs.setdefault("validators", [MinValueValidator(0)])
    return models.DecimalField(**kwargs)


def _uuid_field():
    """
    Champ de synchro (§7.1) : unique et indexé, mais PAS la clé primaire — on garde l'AutoField
    de Django en PK (rowid SQLite, FK internes compactes). `default` sert aux objets nés côté
    serveur (admin, seed, import) ; l'endpoint de sync (phase 2) acceptera l'uuid fourni par le client.
    """
    return models.UUIDField(
        unique=True, db_index=True, default=uuid.uuid4, editable=False
    )


class Foyer(models.Model):
    nom = models.CharField(max_length=100)
    slug = AutoSlugField(unique=True, populate_from="nom")
    membres = models.ManyToManyField(Profil, related_name="foyers")
    archive = models.BooleanField(default=False)
    date_creation = models.DateTimeField("date de création", auto_now_add=True)

    class Meta:
        ordering = ("nom",)

    def __str__(self):
        return self.nom


class Magasin(models.Model):
    foyer = models.ForeignKey(Foyer, on_delete=models.CASCADE, related_name="magasins")
    nom = models.CharField(max_length=100)
    enseigne = models.CharField(max_length=100, blank=True)
    actif = models.BooleanField(default=True)

    class Meta:
        ordering = ("nom",)

    def __str__(self):
        return self.nom


class Rayon(models.Model):
    foyer = models.ForeignKey(Foyer, on_delete=models.CASCADE, related_name="rayons")
    nom = models.CharField(max_length=100)
    ordre = models.PositiveIntegerField(default=0, db_index=True)
    couleur = ColorField(default="#FFFFFF")
    icone = IconField("icône", blank=True)

    class Meta:
        ordering = ("ordre",)
        unique_together = ("foyer", "nom")

    def __str__(self):
        return self.nom


class Etiquette(models.Model):
    foyer = models.ForeignKey(
        Foyer, on_delete=models.CASCADE, related_name="etiquettes"
    )
    nom = models.CharField(max_length=50)
    couleur = ColorField(default="#FFFFFF")

    uuid = _uuid_field()
    modifie_le = models.DateTimeField(auto_now=True)
    supprime_le = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("nom",)
        verbose_name = "étiquette"
        constraints = [
            # Conditionnelle et non unique_together : supprimer « Apéro » (soft delete) puis en
            # recréer une du même nom ne doit pas heurter le tombstone (§5, note soft delete + unicité).
            models.UniqueConstraint(
                fields=["foyer", "nom"],
                condition=models.Q(supprime_le__isnull=True),
                name="nom_unique_par_foyer_hors_supprimees",
            )
        ]

    def __str__(self):
        return self.nom


class Article(models.Model):
    class Unite(models.TextChoices):
        UNITE = "unite", "unité"
        KG = "kg", "kg"
        G = "g", "g"
        L = "l", "L"
        ML = "ml", "mL"
        PAQUET = "paquet", "paquet"
        BOITE = "boite", "boîte"
        SACHET = "sachet", "sachet"
        BOUTEILLE = "bouteille", "bouteille"

    foyer = models.ForeignKey(Foyer, on_delete=models.CASCADE, related_name="articles")
    nom = models.CharField(max_length=150)
    rayon = models.ForeignKey(
        Rayon,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="articles",
    )
    etiquettes = models.ManyToManyField(Etiquette, blank=True, related_name="articles")

    unite = models.CharField(
        max_length=10,
        choices=Unite.choices,
        default="",
        blank=True,
        help_text="Laissé vide par l'import (§9) tant que l'unité n'est pas confirmée.",
    )
    conditionnement = _quantite_field(
        default=1,
        help_text="Unités de conso par unité d'achat (ex. 1,5 pour une bouteille de 1,5 L).",
    )

    stock_cible = _quantite_field(
        default=0, help_text="Niveau normal souhaité à la maison (le « want » du POC)."
    )
    stock_reference = _quantite_field(
        default=0,
        help_text="Stock figé au dernier achat/recalage (le « have » du POC).",
    )
    stock_maj_le = models.DateTimeField(null=True, blank=True)

    conso_par_jour_estimee = _quantite_field(null=True, blank=True)
    conso_amorce = _quantite_field(
        null=True,
        blank=True,
        help_text="Graine de démarrage, lue uniquement tant que conso_par_jour_estimee est vide.",
    )
    suivi_auto = models.BooleanField("suivi automatique", default=True)

    actif = models.BooleanField(default=True)
    note = models.TextField(blank=True)

    uuid = _uuid_field()
    modifie_le = models.DateTimeField(auto_now=True)
    supprime_le = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("nom",)

    def __str__(self):
        return self.nom


class Sortie(models.Model):
    class Source(models.TextChoices):
        MANUEL = "manuel", "Manuel"
        TICKET = "ticket", "Ticket de caisse"
        DRIVE = "drive", "Drive"

    foyer = models.ForeignKey(Foyer, on_delete=models.CASCADE, related_name="sorties")
    nom = models.CharField(max_length=100, blank=True)
    magasin = models.ForeignKey(
        Magasin,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="sorties",
    )
    cree_par = models.ForeignKey(
        Profil, on_delete=models.PROTECT, related_name="sorties_creees"
    )
    cree_le = models.DateTimeField(auto_now_add=True)
    cloture_le = models.DateTimeField(null=True, blank=True)
    source = models.CharField(
        max_length=10, choices=Source.choices, default=Source.MANUEL
    )

    uuid = _uuid_field()
    modifie_le = models.DateTimeField(auto_now=True)
    supprime_le = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-cree_le",)

    def __str__(self):
        return self.nom or f"Sortie du {self.cree_le:%d/%m/%Y}"


class DemandePonctuelle(models.Model):
    article = models.ForeignKey(
        Article, on_delete=models.CASCADE, related_name="demandes_ponctuelles"
    )
    profil = models.ForeignKey(
        Profil, on_delete=models.CASCADE, related_name="demandes_ponctuelles"
    )
    quantite = _quantite_field(default=1)
    date = models.DateTimeField(auto_now_add=True)
    sortie = models.ForeignKey(
        Sortie,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="demandes_ponctuelles",
    )
    satisfaite_par = models.ForeignKey(
        "Ligne",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="demandes_satisfaites",
    )

    uuid = _uuid_field()
    modifie_le = models.DateTimeField(auto_now=True)
    supprime_le = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-date",)
        verbose_name = "demande ponctuelle"

    def __str__(self):
        return f"{self.article} x{self.quantite} ({self.profil})"


class Ligne(models.Model):
    class Origine(models.TextChoices):
        MANUEL = "manuel", "Manuel"
        SEUIL = "seuil", "Seuil"
        SUGGESTION = "suggestion", "Suggestion"
        IMPORT = "import", "Import"

    sortie = models.ForeignKey(Sortie, on_delete=models.CASCADE, related_name="lignes")
    article = models.ForeignKey(
        Article, on_delete=models.CASCADE, related_name="lignes"
    )
    quantite = _quantite_field(default=1)

    cochee_le = models.DateTimeField(null=True, blank=True)
    cochee_par = models.ForeignKey(
        Profil,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="lignes_cochees",
    )
    indisponible_le = models.DateTimeField(null=True, blank=True)

    article_magasin = models.ForeignKey(
        "ArticleMagasin",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="lignes",
    )
    prix_unitaire = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
    )
    origine = models.CharField(
        max_length=10, choices=Origine.choices, default=Origine.MANUEL
    )

    uuid = _uuid_field()
    modifie_le = models.DateTimeField(auto_now=True)
    supprime_le = models.DateTimeField(null=True, blank=True)

    class Meta:
        # Pas d'ordering par rayon ici : rayon est nullable (NULL trie en premier sur SQLite,
        # alors que le §9 veut les articles sans rayon en fin de liste sous « Sans rayon »), et
        # ce lookup imposerait un JOIN à deux niveaux à tous les querysets de Ligne. C'est une
        # préoccupation de vue (phase 1) : F("article__rayon__ordre").asc(nulls_last=True).
        constraints = [
            # Attrape le doublon fréquent (même article deux fois dans la même sortie).
            # « Un article dans une seule sortie ouverte » (§5.1) reste applicatif : une
            # contrainte dure sur cet état global rejetterait en push un geste hors ligne
            # pourtant valide (même article ajouté à deux sorties par deux personnes).
            models.UniqueConstraint(
                fields=["sortie", "article"], name="un_article_une_fois_par_sortie"
            )
        ]

    def __str__(self):
        return f"{self.article} x{self.quantite} ({self.sortie})"


class MouvementStock(models.Model):
    class Type(models.TextChoices):
        ACHAT = "achat", "Achat"
        RECALAGE = "recalage", "Recalage"
        PERTE = "perte", "Perte"

    article = models.ForeignKey(
        Article, on_delete=models.CASCADE, related_name="mouvements"
    )
    type = models.CharField(max_length=10, choices=Type.choices)
    ligne = models.ForeignKey(
        Ligne,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="mouvements",
        help_text="La Ligne à l'origine de ce mouvement — sans elle, « Corriger » ne peut rien défaire.",
    )
    quantite = _quantite_field(
        help_text=(
            "Toujours positive — le type porte le signe : achat = ajoutée au stock, "
            "perte = retirée du stock, recalage = NOUVELLE VALEUR ABSOLUE du stock "
            "(ni un ajout ni un retrait)."
        )
    )
    date = models.DateTimeField(default=timezone.now)
    profil = models.ForeignKey(
        Profil,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="mouvements_stock",
    )
    commentaire = models.CharField(max_length=255, blank=True)

    uuid = _uuid_field()
    modifie_le = models.DateTimeField(auto_now=True)
    supprime_le = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-date",)
        verbose_name = "mouvement de stock"

    def __str__(self):
        return f"{self.get_type_display()} {self.article} x{self.quantite}"


class ArticleMagasin(models.Model):
    article = models.ForeignKey(
        Article, on_delete=models.CASCADE, related_name="articles_magasin"
    )
    magasin = models.ForeignKey(
        Magasin, on_delete=models.CASCADE, related_name="articles_magasin"
    )
    libelle = models.CharField(
        max_length=200, help_text="Tel que le ticket ou le drive l'écrit."
    )
    marque = models.CharField(max_length=100, blank=True)
    code_barre = models.CharField(max_length=20, blank=True)
    vu_le = models.DateTimeField(auto_now=True)
    occurrences = models.PositiveIntegerField(default=1)

    class Meta:
        # (magasin, libelle) et non (article, magasin) : plusieurs libellés (ticket vs drive)
        # doivent pouvoir pointer vers le même article dans le même magasin — cf. conception.md §5.
        unique_together = ("magasin", "libelle")
        ordering = ("libelle",)
        verbose_name = "article en magasin"
        verbose_name_plural = "articles en magasin"

    def __str__(self):
        return self.libelle
