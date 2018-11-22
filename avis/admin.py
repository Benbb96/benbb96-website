from django.contrib import admin
from django.db import models
from django.utils.html import format_html

from avis.forms import AvisForm
from .models import Profil, Restaurant, Plat, Avis


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
    list_display = ('nom', 'apercu_informations', 'adresse', 'position_map', 'telephone', 'nb_plat', 'moyenne', 'date_creation')
    search_fields = ('nom', 'adresse')
    date_hierarchy = 'date_creation'
    ordering = ('nom', 'date_creation')
    prepopulated_fields = {'slug': ('nom',), }

    inlines = [
        PlatInLine,
    ]

    def get_queryset(self, request):
        # Ajoute la moyenne et le nombre de plat sur chacun des restaurants
        qs = super(RestaurantAdmin, self).get_queryset(request)
        qs = qs.annotate(moyenne=models.Avg('plat__avis__note'))
        qs = qs.annotate(nb_plat=models.Count('plat'))
        return qs

    def moyenne(self, restaurant):
        return restaurant.note_moyenne
    moyenne.admin_order_field = 'moyenne'

    def nb_plat(self, restaurant):
        return restaurant.plat_set.count()
    nb_plat.admin_order_field = 'nb_plat'

    nb_plat.short_description = 'Nombre de plat'

    def position_map(self, instance):
        if instance.adresse is not None:
            # TODO Maybe need to add client ID and signature
            return format_html('<img src="http://maps.googleapis.com/maps/api/staticmap?key=AIzaSyC9uAZiNr9tAg4Y_Vc3xvlpFsCVBB2goEw&center=%(latitude)s,%(longitude)s&zoom=%(zoom)s&size=%(width)sx%(height)s&maptype=roadmap&markers=%(latitude)s,%(longitude)s&sensor=false&visual_refresh=true&scale=%(scale)s" width="%(width)s" height="%(height)s">' % {
                'latitude': instance.adresse.latitude,
                'longitude': instance.adresse.longitude,
                'zoom': 14,
                'width': 100,
                'height': 100,
                'scale': 2
            })


class AvisInLine(admin.StackedInline):
    model = Avis
    fields = ('avis', 'note', 'photo')
    extra = 1
    show_change_link = True
    ordering = ('date_creation',)

    form = AvisForm


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
        # Ajoute la note moyenne du plat et le nombre total d'avis sur chacun des plats
        qs = super(PlatAdmin, self).get_queryset(request)
        qs = qs.annotate(moyenne=models.Avg('avis__note'))
        qs = qs.annotate(total=models.Count('avis__note'))
        return qs

    def save_formset(self, request, form, formset, change):
        if formset.model == Avis:
            avis_set = formset.save(commit=False)
            for avis in avis_set:
                avis.auteur = request.user.profil
                avis.save()
        else:
            formset.save()

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
    list_filter = ('auteur', 'note')
    search_fields = ('plat__nom', 'plat__restaurant__nom', 'auteur__user__username')
    date_hierarchy = 'date_creation'
    autocomplete_fields = ('plat',)
    readonly_fields = ('date_creation', 'date_edition')

    form = AvisForm

    def restaurant(self, avis):
        return avis.plat.restaurant

    restaurant.short_description = "Restaurant"

    def get_form(self, request, obj=None, **kwargs):
        # Pré-rempli automatiquement avec l'utilisateur connecté
        form = super(AvisAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['auteur'].initial = Profil.objects.get(user=request.user)
        return form

    def thumbnail(self, obj):
        if obj.photo:
            return format_html('<img src="{}" height="50px" />', obj.get_photo_url())
        return 'Avis n°' + obj.id
