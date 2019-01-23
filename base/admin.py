from django.contrib import admin
from django.utils.html import format_html

from base.models import Projet, LienReseauSocial


@admin.register(Projet)
class ProjetAdmin(admin.ModelAdmin):
    list_display = ('id', 'nom', 'lien', 'actif')
    list_editable = ('nom', 'lien', 'actif')
    search_fields = ('nom',)
    list_filter = ('actif',)
    ordering = ('id',)


@admin.register(LienReseauSocial)
class LienReseauSocialAdmin(admin.ModelAdmin):
    list_display = ('id', 'reseau_social', 'lien', 'ouvrir_nouvel_onglet', 'actif')
    list_editable = ('reseau_social', 'lien', 'ouvrir_nouvel_onglet', 'actif')
    search_fields = ('reseau_social',)
    list_filter = ('actif',)
    ordering = ('id',)
