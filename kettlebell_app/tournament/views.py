from django.shortcuts import render
from kettlebell_app.tournament.models import Player


def index(request):
    players = Player.objects.all()  # Przykład: pobierz wszystkich graczy
    context = {'players': players}
    return render(request, 'kettlebell_app/index.html', context)
