from django.contrib import admin

from base.models import Profil
from versus.models import Joueur, Jeu, Partie, PartieJoueur


@admin.register(Joueur)
class JoueurAdmin(admin.ModelAdmin):
    list_display = ('nom', 'profil', 'nb_victoire', 'ratio')
    search_fields = ('nom', 'profil__user__username')
    ordering = ('nom',)
    date_hierarchy = 'date_creation'
    prepopulated_fields = {'slug': ('nom',), }


@admin.register(Jeu)
class JeuAdmin(admin.ModelAdmin):
    list_display = ('nom', 'createur', 'date_creation', 'type')
    list_filter = ('type',)
    search_fields = ('nom', 'createur__user__username')
    prepopulated_fields = {'slug': ('nom',), }
    ordering = ('nom',)
    date_hierarchy = 'date_creation'

    def get_changeform_initial_data(self, request):
        return {'createur': request.user}


class PartieJoueurInline(admin.TabularInline):
    model = PartieJoueur
    extra = 2


@admin.register(Partie)
class PartieAdmin(admin.ModelAdmin):
    list_display = ('jeu', 'date')
    list_filter = ('jeu',)
    ordering = ('-date',)
    date_hierarchy = 'date'

    inlines = [PartieJoueurInline]


@admin.register(PartieJoueur)
class PartieJoueurAdmin(admin.ModelAdmin):
    list_display = ('partie', 'joueur', 'score_classement')
    search_fields = ('partie__jeu__nom', 'joueur__user__username', 'score_classement')

