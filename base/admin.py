from django.contrib import admin
from django.utils.html import format_html

from base.forms import TestModelForm
from base.models import Projet, LienReseauSocial, TestModel


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


@admin.register(TestModel)
class TestModelAdmin(admin.ModelAdmin):
    list_display = ('img',)

    form = TestModelForm

    def img(self, obj):
        return format_html('<img src="{}" height="50px" />', obj.get_url())
