from .models import LienReseauSocial


def liens_reseaux_sociaux(request):
    """ Ajoute les liens actifs vers mes réseaux sociaux dans le context processor """
    return {'liens_reseaux_sociaux': LienReseauSocial.objects.filter(actif=True)}