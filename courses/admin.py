from django.contrib import admin

from base.admin import ProfilScopedAdmin, swatch_couleur
from courses.models import (
    Article,
    ArticleMagasin,
    DemandePonctuelle,
    Etiquette,
    Foyer,
    Ligne,
    Magasin,
    MouvementStock,
    Rayon,
    Sortie,
)


class FoyerScopedAdmin(ProfilScopedAdmin):
    """Défaut commun aux modèles de `courses` : le foyer est atteint directement."""

    profil_lookup = "foyer__membres"


@admin.register(Foyer)
class FoyerAdmin(FoyerScopedAdmin):
    profil_lookup = "membres"

    list_display = ("nom", "slug", "archive", "date_creation")
    search_fields = ("nom", "membres__user__username")
    filter_horizontal = ("membres",)
    date_hierarchy = "date_creation"


@admin.register(Magasin)
class MagasinAdmin(FoyerScopedAdmin):
    list_display = ("nom", "foyer", "enseigne", "actif")
    list_filter = ("actif",)
    search_fields = ("nom", "enseigne", "foyer__nom")
    list_select_related = ("foyer",)


@admin.register(Rayon)
class RayonAdmin(FoyerScopedAdmin):
    list_display = ("nom", "foyer", "ordre", "affiche_couleur")
    search_fields = ("nom", "foyer__nom")
    list_select_related = ("foyer",)
    ordering = ("foyer", "ordre")

    @admin.display(ordering="couleur", description="couleur")
    def affiche_couleur(self, instance):
        return swatch_couleur(instance.couleur)


@admin.register(Etiquette)
class EtiquetteAdmin(FoyerScopedAdmin):
    list_display = ("nom", "foyer", "affiche_couleur", "supprime_le")
    list_filter = ("supprime_le",)
    search_fields = ("nom", "foyer__nom")
    list_select_related = ("foyer",)

    @admin.display(ordering="couleur", description="couleur")
    def affiche_couleur(self, instance):
        return swatch_couleur(instance.couleur)


@admin.register(Article)
class ArticleAdmin(FoyerScopedAdmin):
    list_display = (
        "nom",
        "foyer",
        "rayon",
        "unite",
        "stock_cible",
        "stock_reference",
        "suivi_auto",
        "actif",
    )
    list_filter = ("actif", "suivi_auto", "rayon")
    search_fields = ("nom", "foyer__nom")
    list_select_related = ("foyer", "rayon")
    autocomplete_fields = ("rayon",)
    filter_horizontal = ("etiquettes",)


@admin.register(Sortie)
class SortieAdmin(FoyerScopedAdmin):
    list_display = (
        "__str__",
        "foyer",
        "magasin",
        "source",
        "cree_par",
        "cree_le",
        "cloture_le",
    )
    list_filter = ("source",)
    search_fields = ("nom", "foyer__nom")
    list_select_related = ("foyer", "magasin", "cree_par__user")
    date_hierarchy = "cree_le"
    autocomplete_fields = ("cree_par",)


@admin.register(DemandePonctuelle)
class DemandePonctuelleAdmin(FoyerScopedAdmin):
    profil_lookup = "article__foyer__membres"

    list_display = ("article", "profil", "quantite", "date", "sortie", "satisfaite_par")
    search_fields = ("article__nom", "profil__user__username")
    list_select_related = ("article", "profil__user", "sortie")
    autocomplete_fields = ("article", "profil", "sortie", "satisfaite_par")
    date_hierarchy = "date"


@admin.register(Ligne)
class LigneAdmin(FoyerScopedAdmin):
    profil_lookup = "sortie__foyer__membres"

    list_display = (
        "sortie",
        "article",
        "quantite",
        "cochee_le",
        "indisponible_le",
        "origine",
    )
    list_filter = ("origine",)
    search_fields = ("article__nom", "sortie__nom")
    list_select_related = ("sortie", "article")
    autocomplete_fields = ("sortie", "article", "article_magasin")


@admin.register(MouvementStock)
class MouvementStockAdmin(FoyerScopedAdmin):
    profil_lookup = "article__foyer__membres"

    list_display = ("article", "type", "quantite", "date", "profil", "ligne")
    list_filter = ("type",)
    search_fields = ("article__nom", "commentaire")
    list_select_related = ("article", "profil__user", "ligne")
    autocomplete_fields = ("article", "ligne", "profil")
    date_hierarchy = "date"


@admin.register(ArticleMagasin)
class ArticleMagasinAdmin(FoyerScopedAdmin):
    profil_lookup = "magasin__foyer__membres"

    list_display = ("libelle", "magasin", "article", "marque", "occurrences", "vu_le")
    search_fields = ("libelle", "marque", "article__nom", "magasin__nom")
    list_select_related = ("magasin", "article")
    autocomplete_fields = ("article", "magasin")
