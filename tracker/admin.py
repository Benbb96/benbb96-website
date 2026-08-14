from django.contrib import admin

from tracker.models import Track, Tracker


class TrackInline(admin.TabularInline):
    model = Track


@admin.register(Tracker)
class TrackerAdmin(admin.ModelAdmin):
    list_display = ("nom", "createur", "icone", "color", "type", "date_creation")
    list_filter = ("type",)
    search_fields = ("createur__user__username", "nom")
    date_hierarchy = "date_creation"
    ordering = ("-date_creation",)

    inlines = [TrackInline]

    def get_changeform_initial_data(self, request):
        return {"createur": request.user}


@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    list_display = ("id", "tracker", "datetime", "valeur", "commentaire")
    date_hierarchy = "datetime"
    ordering = ("-datetime",)
    search_fields = ("tracker__nom", "commentaire")
