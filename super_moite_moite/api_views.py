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


# Palette de couleurs distinctes attribuées automatiquement aux nouvelles
# catégories (le défaut modèle est blanc = invisible sur les graphes/donuts).
CATEGORIE_PALETTE = [
    '#2563eb', '#16a34a', '#dc2626', '#d97706', '#7c3aed',
    '#0ea5e9', '#db2777', '#65a30d', '#0d9488', '#f59e0b',
]


class CategorieView(ModelViewSet):
    serializer_class = CategorieSerializer

    def get_queryset(self):
        return Categorie.objects.filter(logement__habitants=self.request.user.profil)

    def perform_create(self, serializer):
        # Attribue une couleur auto (cyclique par logement) si le client n'en
        # fournit pas, pour éviter deux créations consécutives de la même couleur
        # et des donuts blancs sur blanc.
        couleur = serializer.validated_data.get('couleur')
        if not couleur:
            logement = serializer.validated_data.get('logement')
            index = logement.categories.count() if logement else 0
            couleur = CATEGORIE_PALETTE[index % len(CATEGORIE_PALETTE)]
            serializer.save(couleur=couleur)
        else:
            serializer.save()


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
