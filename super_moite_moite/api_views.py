from rest_framework.viewsets import ModelViewSet

from super_moite_moite.models import Logement, Categorie, Tache
from super_moite_moite.serializers import LogementSerializer, CategorieSerializer, TacheSerializer


class LogementView(ModelViewSet):
    queryset = Logement.objects.all()
    serializer_class = LogementSerializer

    def get_queryset(self):
        return self.request.user.profil.logements.all()


class CategorieView(ModelViewSet):
    queryset = Categorie.objects.all()
    serializer_class = CategorieSerializer

    def get_queryset(self):
        return Categorie.objects.filter(logement__habitants=self.request.user.profil)


class TacheView(ModelViewSet):
    queryset = Tache.objects.all()
    serializer_class = TacheSerializer

    def get_queryset(self):
        return Categorie.objects.filter(categorie__logement__habitants=self.request.user.profil)


# TODO Faire le reste
