from django.contrib import admin

from base.models import Projet


@admin.register(Projet)
class ProjetAdmin(admin.ModelAdmin):
    list_display = ('nom', 'lien', 'actif')
    search_fields = ('nom',)
    list_filter = ('actif',)
