from django.contrib import admin

from base.admin import PhotoAdminAbtract, ProfilScopedAdmin, swatch_couleur
from super_moite_moite.forms import TacheForm
from super_moite_moite.models import Categorie, Logement, PointTache, Tache, TrackTache


class CategorieInlineAdmin(admin.TabularInline):
    model = Categorie
    show_change_link = True


@admin.register(Logement)
class LogementAdmin(ProfilScopedAdmin):
    profil_lookup = "habitants"

    list_display = ("nom", "slug", "date_creation")
    search_fields = ("nom", "habitants__user__username")
    date_hierarchy = "date_creation"
    prepopulated_fields = {
        "slug": ("nom",),
    }

    inlines = (CategorieInlineAdmin,)


class TacheInlineAdmin(admin.StackedInline):
    model = Tache
    form = TacheForm
    show_change_link = True


@admin.register(Categorie)
class CategorieAdmin(ProfilScopedAdmin):
    profil_lookup = "logement__habitants"

    list_display = ("nom", "logement", "order", "affiche_couleur")
    search_fields = ("nom", "logement__nom")
    list_select_related = ("logement",)

    inlines = (TacheInlineAdmin,)

    @admin.display(ordering="couleur", description="couleur")
    def affiche_couleur(self, instance):
        return swatch_couleur(instance.couleur)


class PointTacheInlineAdmin(admin.TabularInline):
    model = PointTache
    autocomplete_fields = ("profil",)


@admin.register(Tache)
class TacheAdmin(ProfilScopedAdmin, PhotoAdminAbtract):
    profil_lookup = "categorie__logement__habitants"

    list_display = ("thumbnail", "nom", "categorie", "order")
    search_fields = ("nom", "categorie__nom", "categorie__logement__nom")
    fields = ("nom", "categorie", "description", "photo")
    list_select_related = ("categorie",)

    form = TacheForm

    inlines = (PointTacheInlineAdmin,)


@admin.register(PointTache)
class PointTacheAdmin(ProfilScopedAdmin):
    profil_lookup = "tache__categorie__logement__habitants"

    list_display = ("profil", "tache", "point")
    list_filter = ("point",)
    list_select_related = ("profil", "tache")
    autocomplete_fields = ("profil", "tache")
    search_fields = (
        "tache__nom",
        "tache__categorie__nom",
        "tache__categorie__logement__nom",
        "profil__user__username",
    )


@admin.register(TrackTache)
class TrackTacheAdmin(ProfilScopedAdmin):
    # Était "…__habitants_" (underscore parasite, depuis 2020) : FieldError pour tout
    # utilisateur staff non-superuser. Jamais vu, faute d'être passé par ce chemin.
    profil_lookup = "tache__categorie__logement__habitants"

    list_display = ("id", "tache", "profil", "datetime", "commentaire")
    list_filter = ("datetime",)
    list_select_related = ("profil", "tache")
    date_hierarchy = "datetime"
    ordering = ("-datetime",)
    search_fields = (
        "tache__nom",
        "tache__categorie__nom",
        "tache__categorie__logement__nom",
        "commentaire",
        "profil__user__username",
    )

    def get_changeform_initial_data(self, request):
        return {"profil": request.user.profil}
