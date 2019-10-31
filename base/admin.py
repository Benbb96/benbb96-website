from adminsortable.admin import NonSortableParentAdmin, SortableTabularInline
from django.contrib import admin

from base.models import Projet, LienReseauSocial, Profil
from tracker.models import Tracker


class TrackerInline(SortableTabularInline):
    model = Tracker


@admin.register(Profil)
class ProfilAdmin(NonSortableParentAdmin):
    list_display = ('user', 'nbAvis', 'note_moyenne', 'age', 'date_creation')
    search_fields = ('user__username',)
    ordering = ('user',)

    inlines = [TrackerInline]

    def nbAvis(self, profil):
        return profil.avis_set.count()

    nbAvis.short_description = "Nombre d'avis"


@admin.register(Projet)
class ProjetAdmin(admin.ModelAdmin):
    list_display = ('id', 'nom', 'lien', 'actif', 'logged_only', 'staff_only')
    list_editable = ('nom', 'lien', 'actif', 'logged_only', 'staff_only')
    search_fields = ('nom',)
    list_filter = ('actif', 'logged_only', 'staff_only')
    ordering = ('id',)


@admin.register(LienReseauSocial)
class LienReseauSocialAdmin(admin.ModelAdmin):
    list_display = ('id', 'reseau_social', 'lien', 'ouvrir_nouvel_onglet', 'actif')
    list_editable = ('reseau_social', 'lien', 'ouvrir_nouvel_onglet', 'actif')
    search_fields = ('reseau_social',)
    list_filter = ('actif',)
    ordering = ('id',)
