from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from .models import (
    BestSeeSawPressResult,
    Category,
    KBSquatResult,
    OverallResult,
    Player,
    SeeSawPressResult,
    SnatchResult,
    SportClub,
    TGUResult,
)
from .resources import PlayerExportResource, PlayerImportResource


@admin.register(Player)
class PlayerAdmin(ImportExportModelAdmin):
    resource_class = PlayerImportResource
    list_display = (
        "name",
        "surname",
        "weight",
        "club",
        "get_categories",
        "snatch_kettlebell_weight",
        "snatch_repetitions",
        "tgu_weight",
        "get_best_see_saw_press_left",
        "get_best_see_saw_press_right",
        "kb_squat_weight",
        "tiebreak",
    )
    list_filter = ("club", "categories", "tiebreak")
    search_fields = ("name", "surname", "club__name", "categories__name")

    fieldsets = (
        (
            "Basic Info",
            {"fields": ("name", "surname", "weight", "club", "categories", "tiebreak")},
        ),
        ("Snatch", {"fields": ("snatch_kettlebell_weight", "snatch_repetitions")}),
        ("TGU", {"fields": ("tgu_weight",)}),
        (
            "See Saw Press",
            {
                "fields": (
                    ("see_saw_press_weight_left_1", "see_saw_press_weight_right_1"),
                    ("see_saw_press_weight_left_2", "see_saw_press_weight_right_2"),
                    ("see_saw_press_weight_left_3", "see_saw_press_weight_right_3"),
                )
            },
        ),
        ("KB Squat", {"fields": ("kb_squat_weight",)}),
    )

    def get_categories(self, obj):
        return ", ".join([category.name for category in obj.categories.all()])

    get_categories.short_description = "Kategoria"

    def get_best_see_saw_press_left(self, obj):
        best_result = BestSeeSawPressResult.objects.filter(player=obj).first()
        return best_result.best_left if best_result else 0

    get_best_see_saw_press_left.short_description = "See Saw Press Left (Best)"

    def get_best_see_saw_press_right(self, obj):
        best_result = BestSeeSawPressResult.objects.filter(player=obj).first()
        return best_result.best_right if best_result else 0

    get_best_see_saw_press_right.short_description = "See Saw Press Right (Best)"

    def get_import_resource_class(self):
        return PlayerImportResource

    def get_export_resource_class(self):
        return PlayerExportResource


@admin.register(SportClub)
class SportClubAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(SnatchResult)
class SnatchResultAdmin(admin.ModelAdmin):
    list_display = ("player", "result", "position")


@admin.register(TGUResult)
class TGUResultAdmin(admin.ModelAdmin):
    list_display = ("player", "result", "position")


@admin.register(SeeSawPressResult)
class SeeSawPressResultAdmin(admin.ModelAdmin):
    list_display = (
        "player",
        "result_left_1",
        "result_left_2",
        "result_left_3",
        "result_right_1",
        "result_right_2",
        "result_right_3",
        "position",
    )


@admin.register(KBSquatResult)
class KBSquatResultAdmin(admin.ModelAdmin):
    list_display = ("player", "result", "position")


@admin.register(OverallResult)
class OverallResultAdmin(admin.ModelAdmin):
    list_display = (
        "player",
        "snatch_points",
        "tgu_points",
        "see_saw_press_points",
        "kb_squat_points",
        "tiebreak_points",
        "total_points",
        "final_position",
    )


@admin.register(BestSeeSawPressResult)
class BestSeeSawPressResultAdmin(admin.ModelAdmin):
    list_display = ("player", "best_left", "best_right")
