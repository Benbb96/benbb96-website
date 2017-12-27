from django.contrib import admin
from .models import Profil, Restaurant, Plat, Tag, Avis

class ProfilAdmin(admin.ModelAdmin):
    list_display = ('user', 'nbAvis', 'date')
    search_fields = ('user__username',)
    ordering = ('user',)

    def nbAvis(self, profil):
        return profil.avis_set.count()

    nbAvis.short_description = "Nombre d'avis"

class PlatInLine(admin.TabularInline):
    model = Plat
    exclude = ('photo', )
    extra = 1

class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('nom', 'apercu_informations', 'adresse', 'telephone', 'nbPLat', 'date')
    search_fields = ('nom', 'adresse')
    date_hierarchy = 'date'
    ordering = ('nom', 'date')

    inlines = [
        PlatInLine,
    ]

    def apercu_informations(self, restaurant):
        text = restaurant.informations[0:40]
        if len(restaurant.informations) > 40:
            return '%s…' % text
        else:
            return text

    apercu_informations.short_description = 'Aperçu des informations'

    def nbPLat(self, restaurant):
        return restaurant.plat_set.count()

    nbPLat.short_description = 'Nombre de plat'

class AvisInLine(admin.TabularInline):
    model = Avis
    exclude = ('photo', )
    extra = 1

class PlatAdmin(admin.ModelAdmin):
    list_display = ('nom', 'restaurant', 'apercu_description', 'prix', 'nbAvis', 'date')
    list_filter = ('restaurant', )
    search_fields = ('nom', )
    date_hierarchy = 'date'
    ordering = ('nom', 'date')

    inlines = [
        AvisInLine,
    ]

    def apercu_description(self, plat):
        """
        Retourne les 40 premiers caractères du contenu de l'article. S'il
        y a plus de 40 caractères, il faut rajouter des points de suspension.
        """
        text = plat.description[0:40]
        if len(plat.description) > 40:
            return '%s…' % text
        else:
            return text

    apercu_description.short_description = 'Description'

    def nbAvis(self, plat):
        return plat.avis_set.count()

    nbAvis.short_description = "Nombre d'avis"
    
class AvisAdmin(admin.ModelAdmin):
    list_display = ('id', 'plat', 'auteur', 'apercu_avis', 'note', 'date')
    list_filter = ('plat', 'auteur', 'note')
    search_fields = ('plat__nom', 'plat__restaurant__nom', 'auteur__user__username')
    ordering = ('date', )
    date_hierarchy = 'date'

    def apercu_avis(self, avis):
        """
        Retourne les 40 premiers caractères du contenu de l'article. S'il
        y a plus de 40 caractères, il faut rajouter des points de suspension.
        """
        text = avis.avis[0:40]
        if len(avis.avis) > 40:
            return '%s…' % text
        else:
            return text

    apercu_avis.short_description = "Aperçu de l'avis"

admin.site.register(Profil, ProfilAdmin)
admin.site.register(Restaurant, RestaurantAdmin)
admin.site.register(Plat, PlatAdmin)
admin.site.register(Tag)
admin.site.register(Avis, AvisAdmin)