from django.shortcuts import render
from .models import Player  # Importuj inne modele, jeśli są potrzebne


def index(request):
    players = Player.objects.all()  # Przykład: pobierz wszystkich graczy
    context = {'players': players}
    return render(request, 'kettlebell_app/index.html', context)
