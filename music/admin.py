from django.contrib import admin
from django.contrib.auth.models import User

from music.models import Pays, Artiste, Style, Label


@admin.register(Pays)
class PaysAdmin(admin.ModelAdmin):
    list_display = ('nom',)
    search_fields = ('nom',)


@admin.register(Style)
class PaysAdmin(admin.ModelAdmin):
    list_display = ('nom',)
    search_fields = ('nom',)


@admin.register(Artiste)
class TrackerAdmin(admin.ModelAdmin):
    list_display = ('nom_artiste', 'nom', 'prenom', 'ville', 'pays', 'date_creation', 'date_modification')
    list_filter = ('styles', 'labels')
    search_fields = (
        'createur__username', 'nom_artiste', 'prenom', 'nom', 'ville', 'pays__nom', 'labels__nom', 'styles__nom'
    )
    date_hierarchy = 'date_creation'
    ordering = ('-date_modification',)
    prepopulated_fields = {'slug': ('nom_artiste',), }

    def get_form(self, request, obj=None, **kwargs):
        # Pré-rempli automatiquement avec l'utilisateur connecté
        form = super(TrackerAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['createur'].initial = User.objects.get(id=request.user.id)
        return form


@admin.register(Label)
class PaysAdmin(admin.ModelAdmin):
    list_display = ('nom',)
    search_fields = ('nom',)
