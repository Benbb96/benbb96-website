from rest_framework import serializers

from tracker.models import Track


class TrackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Track
        exclude = ('tracker',)
