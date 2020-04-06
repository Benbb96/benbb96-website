from rest_framework import serializers

from tracker.models import Tracker, Track


class TrackerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tracker
        fields = ('id', 'createur', 'nom', 'icone', 'color', 'date_creation', 'order')


class TrackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Track
        fields = ('tracker', 'datetime', 'commentaire')


class CustomTrackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Track
        exclude = ('tracker',)
