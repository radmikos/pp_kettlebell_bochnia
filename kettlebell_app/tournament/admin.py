from django import forms
from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from .models import (
    AVAILABLE_DISCIPLINES,
    BestKBSquatResult,
    BestSeeSawPressResult,
    Category,
    KBSquatResult,
    OverallResult,
    PistolSquatResult,
    Player,
    SeeSawPressResult,
    SnatchResult,
    SportClub,
    TGUResult,
)
from .resources import PlayerExportResource, PlayerImportResource


class CategoryAdminForm(forms.ModelForm):
    disciplines = forms.MultipleChoiceField(
        choices=AVAILABLE_DISCIPLINES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Konkurencje",
    )

    class Meta:
        model = Category
        fields = ["name", "disciplines"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields["disciplines"].initial = self.instance.get_disciplines()

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.set_disciplines(self.cleaned_data["disciplines"])
        if commit:
            instance.save()
        return instance


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
        "get_tgu_max",
        "get_best_see_saw_press_left",
        "get_best_see_saw_press_right",
        "get_best_kb_squat",
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
        ("TGU", {"fields": ("tgu_weight_1", "tgu_weight_2", "tgu_weight_3")}),
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
        (
            "KB Squat",
            {
                "fields": (
                    ("kb_squat_weight_left_1", "kb_squat_weight_right_1"),
                    ("kb_squat_weight_left_2", "kb_squat_weight_right_2"),
                    ("kb_squat_weight_left_3", "kb_squat_weight_right_3"),
                )
            },
        ),
        (
            "Pistol Squat",
            {
                "fields": (
                    "pistol_squat_weight_1",
                    "pistol_squat_weight_2",
                    "pistol_squat_weight_3",
                )
            },
        ),
    )

    def get_categories(self, obj):
        return ", ".join([category.name for category in obj.categories.all()])

    get_categories.short_description = "Kategoria"

    def get_tgu_max(self, obj):
        return max(obj.tgu_weight_1 or 0, obj.tgu_weight_2 or 0, obj.tgu_weight_3 or 0)

    get_tgu_max.short_description = "TGU Max"

    def get_best_see_saw_press_left(self, obj):
        best_result = BestSeeSawPressResult.objects.filter(player=obj).first()
        return best_result.best_left if best_result else 0

    get_best_see_saw_press_left.short_description = "See Saw Press Left (Best)"

    def get_best_see_saw_press_right(self, obj):
        best_result = BestSeeSawPressResult.objects.filter(player=obj).first()
        return best_result.best_right if best_result else 0

    get_best_see_saw_press_right.short_description = "See Saw Press Right (Best)"

    def get_best_kb_squat(self, obj):
        best_result = BestKBSquatResult.objects.filter(player=obj).first()
        return best_result.best_result if best_result else 0

    get_best_kb_squat.short_description = "KB Squat (Best)"

    def get_import_resource_class(self):
        return PlayerImportResource

    def get_export_resource_class(self):
        return PlayerExportResource

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        # Update or create TGUResult
        tgu_result, created = TGUResult.objects.get_or_create(player=obj)
        tgu_result.result_1 = obj.tgu_weight_1 or 0
        tgu_result.result_2 = obj.tgu_weight_2 or 0
        tgu_result.result_3 = obj.tgu_weight_3 or 0
        tgu_result.save()

        pistol_squat_result, created = PistolSquatResult.objects.get_or_create(
            player=obj
        )
        pistol_squat_result.result_1 = obj.pistol_squat_weight_1 or 0
        pistol_squat_result.result_2 = obj.pistol_squat_weight_2 or 0
        pistol_squat_result.result_3 = obj.pistol_squat_weight_3 or 0
        pistol_squat_result.save()


# @admin.register(SportClub)
# class SportClubAdmin(admin.ModelAdmin):
#     list_display = ("name",)
#
#
# @admin.register(Category)
# class CategoryAdmin(admin.ModelAdmin):
#     form = CategoryAdminForm
#     list_display = ("name", "get_disciplines_display")
#
#     def get_disciplines_display(self, obj):
#         return ", ".join(obj.get_disciplines())
#
#     get_disciplines_display.short_description = "Konkurencje"
#
#
# @admin.register(SnatchResult)
# class SnatchResultAdmin(admin.ModelAdmin):
#     list_display = ("player", "result", "position")


# @admin.register(PistolSquatResult)
# class PistolSquatResultAdmin(admin.ModelAdmin):
#     list_display = (
#         "player",
#         "result_1",
#         "result_2",
#         "result_3",
#         "get_max_result",
#         "get_bw_percentage",
#         "position",
#     )
#     list_filter = ("player__categories",)
#     search_fields = ("player__name", "player__surname")
#
#     def get_max_result(self, obj):
#         return obj.get_max_result()
#
#     get_max_result.short_description = "Max Result"
#
#     def get_bw_percentage(self, obj):
#         return f"{obj.calculate_bw_percentage():.2f}%"

    # get_bw_percentage.short_description = "%BW"


# @admin.register(TGUResult)
# class TGUResultAdmin(admin.ModelAdmin):
#     list_display = (
#         "player",
#         "result_1",
#         "result_2",
#         "result_3",
#         "get_max_result",
#         "get_bw_percentage",
#         "position",
#     )
#     list_filter = ("player__categories",)
#     search_fields = ("player__name", "player__surname")
#
#     def get_max_result(self, obj):
#         return obj.get_max_result()
#
#     get_max_result.short_description = "Max Result"
#
#     def get_bw_percentage(self, obj):
#         return f"{obj.calculate_bw_percentage():.2f}%"
#
#     get_bw_percentage.short_description = "%BW"


# @admin.register(SeeSawPressResult)
# class SeeSawPressResultAdmin(admin.ModelAdmin):
#     list_display = (
#         "player",
#         "result_left_1",
#         "result_left_2",
#         "result_left_3",
#         "result_right_1",
#         "result_right_2",
#         "result_right_3",
#         "position",
#     )


# @admin.register(KBSquatResult)
# class KBSquatResultAdmin(admin.ModelAdmin):
#     list_display = (
#         "player",
#         "get_max_result",
#         "get_result_1",
#         "get_result_2",
#         "get_result_3",
#         "position",
#     )
#
#     def get_max_result(self, obj):
#         return obj.get_max_result()
#
#     get_max_result.short_description = "Max Result"
#
#     def get_result_1(self, obj):
#         return f"L: {obj.result_left_1}, R: {obj.result_right_1}"
#
#     get_result_1.short_description = "Result 1"
#
#     def get_result_2(self, obj):
#         return f"L: {obj.result_left_2}, R: {obj.result_right_2}"
#
#     get_result_2.short_description = "Result 2"
#
#     def get_result_3(self, obj):
#         return f"L: {obj.result_left_3}, R: {obj.result_right_3}"
#
#     get_result_3.short_description = "Result 3"
#
#
# @admin.register(OverallResult)
# class OverallResultAdmin(admin.ModelAdmin):
#     list_display = (
#         "player",
#         "snatch_points",
#         "tgu_points",
#         "see_saw_press_points",
#         "kb_squat_points",
#         "pistol_squat_points",
#         "tiebreak_points",
#         "total_points",
#         "final_position",
#     )


# @admin.register(BestSeeSawPressResult)
# class BestSeeSawPressResultAdmin(admin.ModelAdmin):
#     list_display = ("player", "best_left", "best_right")
#
#
# @admin.register(BestKBSquatResult)
# class BestKBSquatResultAdmin(admin.ModelAdmin):
#     list_display = ("player", "best_result")
