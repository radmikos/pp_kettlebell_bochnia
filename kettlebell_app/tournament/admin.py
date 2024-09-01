from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import Player, SportClub, Category
from .resources import PlayerImportResource, PlayerExportResource

class PlayerAdmin(ImportExportModelAdmin):
    resource_class = PlayerImportResource
    list_display = ('name', 'surname', 'weight', 'club', 'get_categories', 'snatch_kettlebell_weight', 'snatch_repetitions','tgu_weight','see_saw_press_weight_left','see_saw_press_weight_right','kb_squat_weight','tiebreak')
    list_filter = ('club', 'categories', 'tiebreak')
    search_fields = ('name', 'surname', 'club__name', 'categories__name')

    def get_categories(self, obj):
        return ", ".join([category.name for category in obj.categories.all()])
    get_categories.short_description = 'Kategoria'

    def get_import_resource_class(self):
        return PlayerImportResource

    def get_export_resource_class(self):
        return PlayerExportResource

admin.site.register(Player, PlayerAdmin)
admin.site.register(SportClub)
admin.site.register(Category)