from django.contrib import admin
from .models import SportClub, WeightCategory, Level, Player, SnatchResults, TGUResults, SeeSawPressWeight, Results2xKBSQAD

admin.site.register(SportClub)
admin.site.register(WeightCategory)
admin.site.register(Level)
admin.site.register(Player)
admin.site.register(SnatchResults)
admin.site.register(TGUResults)
admin.site.register(SeeSawPressWeight)
admin.site.register(Results2xKBSQAD)