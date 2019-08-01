from django.contrib import admin

from base.models import Profil
from versus.models import Jeu, Partie, PartieJoueur


@admin.register(Jeu)
class JeuAdmin(admin.ModelAdmin):
    list_display = ('nom', 'createur', 'date_creation', 'classement')
    list_filter = ('classement',)
    search_fields = ('nom', 'createur__user__username',)
    prepopulated_fields = {'slug': ('nom',), }
    ordering = ('nom',)
    date_hierarchy = 'date_creation'

    def get_form(self, request, obj=None, **kwargs):
        # Pré-rempli automatiquement avec l'utilisateur connecté
        form = super(JeuAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['createur'].initial = Profil.objects.get(user=request.user)
        return form


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

