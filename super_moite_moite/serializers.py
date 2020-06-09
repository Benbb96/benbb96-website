from rest_framework import serializers

from base.models import Profil
from super_moite_moite.models import Logement, Categorie, Tache, PointTache, TrackTache


class TrackTacheSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrackTache
        fields = '__all__'
        read_only_fields = ('id',)


class ProfilSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    tache_tracks = TrackTacheSerializer(many=True, read_only=True)

    class Meta:
        model = Profil
        fields = ('id', 'user', 'avatar', 'get_absolute_url', 'tache_tracks')
        read_only_fields = fields


class PointTacheSerializer(serializers.ModelSerializer):
    class Meta:
        model = PointTache
        fields = ('id', 'tache', 'profil', 'point')
        read_only_fields = ('id',)


class TacheSerializer(serializers.ModelSerializer):
    tracks = TrackTacheSerializer(many=True, read_only=True)
    point_profils = PointTacheSerializer(many=True, read_only=True)

    class Meta:
        model = Tache
        fields = (
            'id', 'nom', 'description', 'categorie', 'order', 'tracks', 'point_profils', 'photo', 'photo_url'
        )
        read_only_fields = ('id',)


class CategorieSerializer(serializers.ModelSerializer):
    taches = TacheSerializer(many=True, read_only=True)

    class Meta:
        model = Categorie
        fields = '__all__'
        read_only_fields = ('id',)


class LogementSerializer(serializers.ModelSerializer):
    categories = CategorieSerializer(many=True, read_only=True)
    habitants = ProfilSerializer(many=True, read_only=True)

    class Meta:
        model = Logement
        fields = ('id', 'nom', 'date_creation', 'habitants', 'categories')
        read_only_fields = ('id', 'date_creation')
