from rest_framework import serializers

from tracker.models import Tracker, Track


class TrackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Track
        fields = ('id', 'tracker', 'datetime', 'commentaire')


class TrackerSerializer(serializers.ModelSerializer):
    tracks = TrackSerializer(many=True, read_only=True)

    class Meta:
        model = Tracker
        fields = ('id', 'createur', 'nom', 'icone', 'color', 'date_creation', 'order', 'tracks')


class CustomTrackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Track
        exclude = ('tracker',)
