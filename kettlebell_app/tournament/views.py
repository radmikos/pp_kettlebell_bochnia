from django.shortcuts import render
from .models import Player


def index(request):
    players = Player.objects.all()
    context = {'players': players}
    return render(request, 'index.html', context)
