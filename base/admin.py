from adminsortable.admin import NonSortableParentAdmin, SortableTabularInline
from django.contrib import admin
from django.utils.html import format_html

from base.models import LienReseauSocial, Profil, Projet
from tracker.models import Tracker


class TrackerInline(SortableTabularInline):
    model = Tracker


@admin.register(Profil)
class ProfilAdmin(NonSortableParentAdmin):
    list_display = ("user", "nbAvis", "note_moyenne", "age", "date_creation")
    search_fields = ("user__username",)
    ordering = ("user",)

    inlines = [TrackerInline]

    def nbAvis(self, profil):
        return profil.avis_set.count()

    nbAvis.short_description = "Nombre d'avis"


@admin.register(Projet)
class ProjetAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "nom",
        "lien",
        "external",
        "position",
        "actif",
        "logged_only",
        "staff_only",
    )
    list_editable = (
        "nom",
        "lien",
        "external",
        "position",
        "actif",
        "logged_only",
        "staff_only",
    )
    search_fields = ("nom", "lien")
    list_filter = ("actif", "logged_only", "staff_only")


@admin.register(LienReseauSocial)
class LienReseauSocialAdmin(admin.ModelAdmin):
    list_display = ("id", "reseau_social", "lien", "ouvrir_nouvel_onglet", "actif")
    list_editable = ("reseau_social", "lien", "ouvrir_nouvel_onglet", "actif")
    search_fields = ("reseau_social",)
    list_filter = ("actif",)
    ordering = ("id",)


class PhotoAdminAbtract(admin.ModelAdmin):
    def thumbnail(self, obj):
        if obj.photo:
            return format_html('<img src="{}" height="50px" />', obj.photo_url)
        return None


def swatch_couleur(couleur):
    """
    Pastille de couleur pour un `list_display` d'admin (champs ColorField).
    Mutualise le rendu jusque-là recopié dans super_moite_moite, my_spot et courses.
    """
    return format_html(
        '<div style="padding: 5px; background-color: {color}">{color}</div>',
        color=couleur,
    )


class ProfilScopedAdmin(admin.ModelAdmin):
    """
    Restreint la liste d'admin aux objets rattachés au Profil de l'utilisateur — le superuser
    voit tout. `profil_lookup` est le chemin d'ORM depuis CE modèle jusqu'au Profil
    (ex. "logement__habitants", "article__foyer__membres").

    Un lookup erroné ne se voit qu'à l'exécution, et seulement pour un utilisateur
    non-superuser : c'est ainsi qu'un `habitants_` a survécu six ans dans
    super_moite_moite. `smoke_tests.AdminProfilScopeTest` valide désormais chaque lookup.
    """

    profil_lookup = None

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if self.profil_lookup and not request.user.is_superuser:
            queryset = queryset.filter(**{self.profil_lookup: request.user.profil})
        return queryset
