from django.contrib import admin
from django.db import models

from .models import Profil, Restaurant, Plat, Avis


def apercu(text):
    """
    Retourne les 50 premiers caractères du texte donné en paramètre.
    S'il  y a plus de 50 caractères, il faut rajouter des points de suspension.
    """
    apercu = text[0:50]
    if len(text) > 50:
        return '%s...' % apercu
    return apercu


@admin.register(Profil)
class ProfilAdmin(admin.ModelAdmin):
    list_display = ('user', 'nbAvis', 'note_moyenne', 'date_creation')
    search_fields = ('user__username',)
    ordering = ('user',)

    def nbAvis(self, profil):
        return profil.avis_set.count()

    nbAvis.short_description = "Nombre d'avis"


class PlatInLine(admin.StackedInline):
    model = Plat
    exclude = ('photo', )
    extra = 1
    show_change_link = True


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('nom', 'apercu_informations', 'adresse', 'telephone', 'nbPLat', 'note_moyenne', 'date_creation')
    search_fields = ('nom', 'adresse')
    date_hierarchy = 'date_creation'
    ordering = ('nom', 'date_creation')

    inlines = [
        PlatInLine,
    ]

    def apercu_informations(self, restaurant):
        return apercu(restaurant.informations)

    apercu_informations.short_description = 'Aperçu des informations'

    def nbPLat(self, restaurant):
        return restaurant.plat_set.count()

    nbPLat.short_description = 'Nombre de plat'


class AvisInLine(admin.StackedInline):
    model = Avis
    fields = ('auteur', 'avis', 'note', 'photo')
    extra = 1
    show_change_link = True

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # Limite les résultats à l'utilisateur connecté
        if db_field.name == 'auteur':
            kwargs["queryset"] = Profil.objects.filter(user=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Plat)
class PlatAdmin(admin.ModelAdmin):
    list_display = ('nom', 'restaurant', 'apercu_description', 'prix', 'moyenne', 'total_avis')
    list_filter = ('restaurant', )
    search_fields = ('nom', 'description', 'restaurant__nom')
    date_hierarchy = 'date_creation'
    ordering = ('-date_creation',)
    autocomplete_fields = ('restaurant',)

    inlines = [
        AvisInLine,
    ]

    def get_queryset(self, request):
        # Ajoute la note moyenne du plat sur chacun des plats
        qs = super(PlatAdmin, self).get_queryset(request)
        qs = qs.annotate(moyenne=models.Avg('avis__note'))
        qs = qs.annotate(total=models.Count('avis__note'))
        return qs

    def apercu_description(self, plat):
        return apercu(plat.description)

    apercu_description.short_description = 'Description'

    def nbAvis(self, plat):
        return plat.avis_set.count()

    nbAvis.short_description = "Nombre d'avis"

    def moyenne(self, obj):
        return obj.moyenne

    moyenne.admin_order_field = 'moyenne'

    def total_avis(self, obj):
        return obj.total

    total_avis.admin_order_field = 'total'


@admin.register(Avis)
class AvisAdmin(admin.ModelAdmin):
    list_display = ('id', 'restaurant', 'plat', 'auteur', 'apercu_avis', 'note', 'date_creation', 'date_edition')
    list_filter = ('plat', 'auteur', 'note')
    search_fields = ('plat__nom', 'plat__restaurant__nom', 'auteur__user__username')
    ordering = ('-date_edition', )
    date_hierarchy = 'date_creation'
    autocomplete_fields = ('plat',)

    def apercu_avis(self, avis):
        return apercu(avis.avis)

    apercu_avis.short_description = "Aperçu de l'avis"

    def restaurant(self, avis):
        return avis.plat.restaurant

    restaurant.short_description = "Restaurant"

    def get_form(self, request, obj=None, **kwargs):
        # Pré-rempli automatiquement avec l'utilisateur connecté
        form = super(AvisAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['auteur'].initial = Profil.objects.get(user=request.user)
        return form
