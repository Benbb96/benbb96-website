from django.contrib import admin
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
    list_display = ('user', 'nbAvis', 'date_creation')
    search_fields = ('user__username',)
    ordering = ('user',)

    def nbAvis(self, profil):
        return profil.avis_set.count()

    nbAvis.short_description = "Nombre d'avis"


class PlatInLine(admin.TabularInline):
    model = Plat
    exclude = ('photo', )
    extra = 1
    show_change_link = True


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('nom', 'apercu_informations', 'adresse', 'telephone', 'nbPLat', 'date_creation')
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


class AvisInLine(admin.TabularInline):
    model = Avis
    exclude = ('photo', )
    extra = 1
    show_change_link = True


@admin.register(Plat)
class PlatAdmin(admin.ModelAdmin):
    list_display = ('nom', 'restaurant', 'apercu_description', 'prix', 'nbAvis', 'date_creation')
    list_filter = ('restaurant', )
    search_fields = ('nom', 'description', 'restaurant__nom')
    date_hierarchy = 'date_creation'
    ordering = ('-date_creation',)

    inlines = [
        AvisInLine,
    ]

    def apercu_description(self, plat):
        return apercu(plat.description)

    apercu_description.short_description = 'Description'

    def nbAvis(self, plat):
        return plat.avis_set.count()

    nbAvis.short_description = "Nombre d'avis"


@admin.register(Avis)
class AvisAdmin(admin.ModelAdmin):
    list_display = ('id', 'restaurant', 'plat', 'auteur', 'apercu_avis', 'note', 'date_creation', 'date_edition')
    list_filter = ('plat', 'auteur', 'note')
    search_fields = ('plat__nom', 'plat__restaurant__nom', 'auteur__user__username')
    ordering = ('-date_edition', )
    date_hierarchy = 'date_creation'

    def apercu_avis(self, avis):
        return apercu(avis.avis)

    apercu_avis.short_description = "Aperçu de l'avis"

    def restaurant(self, avis):
        return avis.plat.restaurant

    restaurant.short_description = "Restaurant"
