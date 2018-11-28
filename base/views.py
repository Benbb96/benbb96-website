from django.contrib.auth.models import User
from django.shortcuts import render
from django.views.generic import ListView, DetailView
import pyrebase

from base.models import Projet


class ProfilDetailView(DetailView):
    model=User
    template_name='base/profil.html'
    slug_field='username'


class ProjetListView(ListView):
    model = Projet
    template_name = 'base/home.html'


def test_firebase(request):
    config = {
        'apiKey': "AIzaSyBZvRl1Q35AH9j4vYKwTM5YYMUZp6HAjLo",
        'authDomain': "eminent-airport-148108.firebaseapp.com",
        'databaseURL': "https://eminent-airport-148108.firebaseio.com",
        'projectId': "eminent-airport-148108",
        'storageBucket': "eminent-airport-148108.appspot.com",
        'messagingSenderId': "994857141623",
        'serviceAccount': "/home/benjamin/Documents/eminent-airport-148108-firebase-adminsdk-0dvqo-916671b868.json"
    }
    firebase = pyrebase.initialize_app(config)

    storage = firebase.storage()
    # as admin
    url = storage.child("test/bbb.png").get_url(None)
    return render(request, 'base/test.html', {'url': url})
