from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from super_moite_moite.models import Categorie, Tache, PointTache, TrackTache
from super_moite_moite.serializers import LogementSerializer, CategorieSerializer, TacheSerializer, \
    PointTacheSerializer, TrackTacheSerializer, TrackTacheSerializerSansProfil


class LogementView(ModelViewSet):
    serializer_class = LogementSerializer

    def get_queryset(self):
        return self.request.user.profil.logements.all()


class CategorieView(ModelViewSet):
    serializer_class = CategorieSerializer

    def get_queryset(self):
        return Categorie.objects.filter(logement__habitants=self.request.user.profil)


class TacheView(ModelViewSet):
    serializer_class = TacheSerializer

    def get_queryset(self):
        return Tache.objects.filter(categorie__logement__habitants=self.request.user.profil)

    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser, FormParser], url_path='upload_photo')
    def upload_photo(self, request, pk=None):
        tache = self.get_object()
        file = request.FILES.get('photo')
        if not file:
            return Response({'error': 'Aucun fichier fourni.'}, status=400)
        tache.photo = file
        tache.save()
        return Response({'photo_url': tache.photo_url, 'photo': str(tache.photo)})


class PointTacheView(ModelViewSet):
    serializer_class = PointTacheSerializer

    def get_queryset(self):
        return PointTache.objects.filter(tache__categorie__logement__habitants=self.request.user.profil)


class TrackTacheView(ModelViewSet):
    serializer_class = TrackTacheSerializer

    def get_queryset(self):
        return TrackTache.objects.filter(tache__categorie__logement__habitants=self.request.user.profil)

    def get_serializer_class(self):
        if self.action == 'update' or self.action == 'partial_update':
            return super().get_serializer_class()
        return TrackTacheSerializerSansProfil

    def perform_create(self, serializer):
        serializer.save(profil=self.request.user.profil)
