from django.core.exceptions import (
    MultipleObjectsReturned,  # Dodane importy
    ObjectDoesNotExist,
)
from import_export import fields, resources
from import_export.widgets import ForeignKeyWidget, ManyToManyWidget

from .models import Category, Player, SportClub


class CustomForeignKeyWidget(ForeignKeyWidget):
    def clean(self, value, row=None, *args, **kwargs):
        if value:
            try:
                return self.get_queryset(value, row, *args, **kwargs).get(
                    **{self.field: value}
                )
            except self.model.DoesNotExist:
                return self.model.objects.create(**{self.field: value})
            except self.model.MultipleObjectsReturned:
                return self.get_queryset(value, row, *args, **kwargs).first()
        return None


class PlayerImportResource(resources.ModelResource):
    name = fields.Field(column_name="Imię", attribute="name")
    surname = fields.Field(column_name="Nazwisko", attribute="surname")
    weight = fields.Field(column_name="Waga", attribute="weight")
    club = fields.Field(
        column_name="Klub",
        attribute="club",
        widget=CustomForeignKeyWidget(SportClub, "name"),
    )
    categories = fields.Field(
        column_name="Kategoria",
        attribute="categories",
        widget=ManyToManyWidget(Category, field="name", separator=", "),
    )
    snatch_kettlebell_weight = fields.Field(
        column_name="Ciężar kettla (rwanie)", attribute="snatch_kettlebell_weight"
    )
    snatch_repetitions = fields.Field(
        column_name="Liczba powtórzeń (rwanie)", attribute="snatch_repetitions"
    )
    tgu_weight = fields.Field(column_name="Ciężar TGU", attribute="tgu_weight")
    see_saw_press_weight_left = fields.Field(
        column_name="Ciężar See Saw Press (lewa)", attribute="see_saw_press_weight_left"
    )
    see_saw_press_weight_right = fields.Field(
        column_name="Ciężar See Saw Press (prawa)",
        attribute="see_saw_press_weight_right",
    )
    kb_squat_weight = fields.Field(
        column_name="Ciężar KB Squat", attribute="kb_squat_weight"
    )
    tiebreak = fields.Field(column_name="Dogrywka", attribute="tiebreak")

    def before_import_row(self, row, **kwargs):
        try:
            player = Player.objects.get(
                name=row["Imię"], surname=row["Nazwisko"], club__name=row["Klub"]
            )
            # Sprawdź, czy kategoria już jest przypisana
            categories = row["Kategoria"].split(", ")
            for category_name in categories:
                category, created = Category.objects.get_or_create(name=category_name)
                if not player.categories.filter(id=category.id).exists():
                    player.categories.add(category)
            row[
                "skip_row"
            ] = True  # Oznacz wiersz jako przetworzony, aby nie tworzyć duplikatów
        except ObjectDoesNotExist:
            pass
        except MultipleObjectsReturned:
            player = Player.objects.filter(
                name=row["Imię"], surname=row["Nazwisko"], club__name=row["Klub"]
            ).first()

    class Meta:
        model = Player


class PlayerExportResource(resources.ModelResource):
    club = fields.Field(
        column_name="Klub", attribute="club", widget=ForeignKeyWidget(SportClub, "name")
    )
    categories = fields.Field(
        column_name="Kategoria",
        attribute="categories",
        widget=ManyToManyWidget(Category, field="name", separator=", "),
    )
    snatch_results = fields.Field(
        column_name="Wyniki Rwania", attribute="snatch_results"
    )
    tgu_body_percent = fields.Field(
        column_name="TGU % Wagi Ciała", attribute="tgu_body_percent_weight"
    )
    see_saw_press_body_percent_left = fields.Field(
        column_name="See Saw Press % Wagi Ciała (lewa)",
        attribute="see_saw_press_body_percent_weight_left",
    )
    see_saw_press_body_percent_right = fields.Field(
        column_name="See Saw Press % Wagi Ciała (prawa)",
        attribute="see_saw_press_body_percent_weight_right",
    )
    kb_squat_body_percent = fields.Field(
        column_name="KB Squat % Wagi Ciała", attribute="kb_squat_body_percent_weight"
    )

    class Meta:
        model = Player
        fields = (
            "name",
            "surname",
            "weight",
            "club",
            "categories",
            "snatch_kettlebell_weight",
            "snatch_repetitions",
            "snatch_results",
            "tgu_weight",
            "tgu_body_percent",
            "see_saw_press_weight_left",
            "see_saw_press_weight_right",
            "see_saw_press_body_percent_left",
            "see_saw_press_body_percent_right",
            "kb_squat_weight",
            "kb_squat_body_percent",
            "tiebreak",
        )
        export_order = fields

    def dehydrate_snatch_results(self, player):
        return player.snatch_results() if player.snatch_results() is not None else "N/A"

    def dehydrate_tgu_body_percent(self, player):
        return (
            f"{player.tgu_body_percent_weight():.2f}%"
            if player.tgu_body_percent_weight() is not None
            else "N/A"
        )

    def dehydrate_see_saw_press_body_percent_left(self, player):
        return (
            f"{player.see_saw_press_body_percent_weight_left():.2f}%"
            if player.see_saw_press_body_percent_weight_left() is not None
            else "N/A"
        )

    def dehydrate_see_saw_press_body_percent_right(self, player):
        return (
            f"{player.see_saw_press_body_percent_weight_right():.2f}%"
            if player.see_saw_press_body_percent_weight_right() is not None
            else "N/A"
        )

    def dehydrate_kb_squat_body_percent(self, player):
        return (
            f"{player.kb_squat_body_percent_weight():.2f}%"
            if player.kb_squat_body_percent_weight() is not None
            else "N/A"
        )
