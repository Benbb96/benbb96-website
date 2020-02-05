from django.conf import settings
from django.contrib import admin
from django.utils.html import format_html

from base.admin import PhotoAdminAbtract
from my_spot.forms import SpotPhotoForm
from my_spot.models import Spot, SpotTag, SpotPhoto, SpotNote, SpotGroup, SpotGroupProfil


@admin.register(SpotTag)
class SpotTagAdmin(admin.ModelAdmin):
    list_display = ('nom', 'date_creation', 'icone', 'couleur')
    search_fields = ('nom',)
    date_hierarchy = 'date_creation'
    prepopulated_fields = {'slug': ('nom',), }

    def couleur(self, instance):
        return format_html(
            '<div style="padding: 5px; background-color: {color}">{color}</div>',
            color=instance.color
        )
    couleur.admin_order_field = 'color'


class SpotGroupProfilInLine(admin.TabularInline):
    model = SpotGroupProfil


@admin.register(SpotGroup)
class SpotGroupAdmin(admin.ModelAdmin):
    list_display = ('nom', 'slug', 'description', 'count', 'date_creation')
    search_fields = ('nom', 'description', 'profils__user__username')
    ordering = ('nom',)
    date_hierarchy = 'date_creation'
    prepopulated_fields = {'slug': ('nom',), }

    inlines = (SpotGroupProfilInLine,)

    def count(self, obj):
        return obj.profils.count()
    count.short_description = 'Nombre de profil'


class SpotPhotoInLine(admin.StackedInline):
    model = SpotPhoto
    fields = ('photo', 'photographe', 'description')
    extra = 1
    show_change_link = True
    ordering = ('date_ajout',)

    form = SpotPhotoForm

    def get_changeform_initial_data(self, request):
        return {'photographe': request.user}


@admin.register(Spot)
class SpotAdmin(admin.ModelAdmin):
    list_display = ('nom', 'position_map', 'explorateur', 'visibilite', 'date_creation', 'date_modification')
    list_filter = ('visibilite', 'explorateur')
    list_select_related = ('explorateur',)
    search_fields = ('nom', 'description', 'groupes__name', 'tags__nom')
    ordering = ('-date_modification',)
    date_hierarchy = 'date_creation'
    prepopulated_fields = {'slug': ('nom',), }
    autocomplete_fields = ('groupes', 'tags')

    inlines = (SpotPhotoInLine,)

    def position_map(self, instance):
        if instance.position is not None:
            # TODO Maybe need to add client ID and signature
            return format_html('<img src="http://maps.googleapis.com/maps/api/staticmap?key=%(map_api_key)s&center=%(latitude)s,%(longitude)s&zoom=%(zoom)s&size=%(width)sx%(height)s&maptype=roadmap&markers=%(latitude)s,%(longitude)s&sensor=false&visual_refresh=true&scale=%(scale)s" width="%(width)s" height="%(height)s">' % {
                'map_api_key': settings.GEOPOSITION_GOOGLE_MAPS_API_KEY[0],
                'latitude': instance.position.latitude,
                'longitude': instance.position.longitude,
                'zoom': 14,
                'width': 100,
                'height': 100,
                'scale': 2
            })
    position_map.short_description = 'Localisation'

    def get_changeform_initial_data(self, request):
        return {'explorateur': request.user}


@admin.register(SpotPhoto)
class SpotPhotoAdmin(PhotoAdminAbtract):
    list_display = ('thumbnail', 'spot', 'photographe', 'description', 'date_ajout')
    list_select_related = ('spot', 'photographe')
    autocomplete_fields = ('spot', 'photographe')
    search_fields = ('spot__nom', 'description')
    date_hierarchy = 'date_ajout'
    ordering = ('-date_ajout',)

    form = SpotPhotoForm

    def get_changeform_initial_data(self, request):
        return {'photographe': request.user}


@admin.register(SpotNote)
class SpotNoteAdmin(admin.ModelAdmin):
    list_display = ('id', 'spot', 'auteur', 'note', 'justification', 'date_ajout')
    list_filter = ('note',)
    list_select_related = ('spot', 'auteur')
    autocomplete_fields = ('spot', 'auteur')
    date_hierarchy = 'date_ajout'
    search_fields = ('spot__nom', 'justification')

    def get_changeform_initial_data(self, request):
        return {'auteur': request.user}
