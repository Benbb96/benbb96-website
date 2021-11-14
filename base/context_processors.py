from django.conf import settings

from .models import LienReseauSocial


def base_context(request):
    """
    Ajoute les variables de contexte global avec :
      - La clé d'API Google Analytics
      - les liens actifs vers mes réseaux sociaux dans le context processor
    """
    return {
        'GOOGLE_ANALYTICS_KEY': settings.GOOGLE_ANALYTICS_KEY,
        'GEOPOSITION_GOOGLE_MAPS_API_KEY': settings.GEOPOSITION_GOOGLE_MAPS_API_KEY,
        'liens_reseaux_sociaux': LienReseauSocial.objects.filter(actif=True)
    }
