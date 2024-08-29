from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import Player, SportClub, Category
from .resources import PlayerImportResource, PlayerExportResource

class PlayerAdmin(ImportExportModelAdmin):
    resource_class = PlayerImportResource
    list_display = ('name', 'surname', 'club', 'get_categories')
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