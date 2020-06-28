from rest_framework import serializers

from base.templatetags.custom_tags import contrast_color
from tracker.models import Tracker, Track


class TrackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Track
        fields = ('id', 'tracker', 'datetime', 'commentaire')


class TrackerSerializer(serializers.ModelSerializer):
    tracks = TrackSerializer(many=True, read_only=True)
    contrast_color = serializers.SerializerMethodField()

    class Meta:
        model = Tracker
        fields = ('id', 'createur', 'nom', 'icone', 'color', 'contrast_color', 'date_creation', 'order', 'tracks')

    def get_contrast_color(self, tracker):
        return contrast_color(tracker.color)


class CustomTrackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Track
        exclude = ('tracker',)
