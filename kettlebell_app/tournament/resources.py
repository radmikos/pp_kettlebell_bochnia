import logging

from django.core.exceptions import MultipleObjectsReturned
from django.core.exceptions import ObjectDoesNotExist
from import_export import fields, resources
from import_export.widgets import ForeignKeyWidget, ManyToManyWidget

from .models import Category, OverallResult, Player, SportClub

logger = logging.getLogger(__name__)


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

    def before_import_row(self, row, **kwargs):
        logger.info(f"Przetwarzanie wiersza: {row}")
        try:
            player = Player.objects.get(
                name=row["Imię"], surname=row["Nazwisko"], club__name=row["Klub"]
            )
            logger.info(f"Znaleziono istniejącego zawodnika: {player}")

            categories = row["Kategoria"].split(", ")
            for category_name in categories:
                category, created = Category.objects.get_or_create(name=category_name)
                if created:
                    logger.info(f"Utworzono nową kategorię: {category_name}")
                if not player.categories.filter(id=category.id).exists():
                    player.categories.add(category)
                    logger.info(
                        f"Dodano kategorię {category_name} do zawodnika {player}"
                    )
                else:
                    logger.info(
                        f"Kategoria {category_name} już istnieje dla zawodnika {player}"
                    )

            row["skip_row"] = True
            logger.info(f"Wiersz oznaczony do pominięcia dla zawodnika {player}")
        except ObjectDoesNotExist:
            logger.info(
                f"Nie znaleziono istniejącego zawodnika dla: {row['Imię']} {row['Nazwisko']} z klubu {row['Klub']}"
            )
        except MultipleObjectsReturned:
            logger.warning(
                f"Znaleziono wielu zawodników dla: {row['Imię']} {row['Nazwisko']} z klubu {row['Klub']}"
            )
            player = Player.objects.filter(
                name=row["Imię"], surname=row["Nazwisko"], club__name=row["Klub"]
            ).first()
            logger.info(f"Wybrano pierwszego znalezionego zawodnika: {player}")
        except Exception as e:
            logger.error(
                f"Wystąpił nieoczekiwany błąd podczas przetwarzania wiersza: {e}"
            )

    class Meta:
        model = Player
        fields = ("name", "surname", "club", "categories")
        import_id_fields = ["name", "surname", "club"]


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
    snatch_position = fields.Field(
        column_name="Miejsce Rwanie", attribute="snatch_position"
    )

    tgu_body_percent = fields.Field(
        column_name="TGU % Wagi Ciała", attribute="tgu_body_percent_weight"
    )
    tgu_position = fields.Field(column_name="Miejsce TGU", attribute="tgu_position")

    see_saw_press_body_percent_left = fields.Field(
        column_name="See Saw Press % Wagi Ciała (lewa)",
        attribute="see_saw_press_body_percent_weight_left",
    )
    see_saw_press_body_percent_right = fields.Field(
        column_name="See Saw Press % Wagi Ciała (prawa)",
        attribute="see_saw_press_body_percent_weight_right",
    )
    see_saw_press_position = fields.Field(
        column_name="Miejsce See Saw Press", attribute="see_saw_press_position"
    )

    kb_squat_body_percent = fields.Field(
        column_name="KB Squat % Wagi Ciała", attribute="kb_squat_body_percent_weight"
    )
    kb_squat_position = fields.Field(
        column_name="Miejsce KB Squat", attribute="kb_squat_position"
    )

    pistol_squat_weight = fields.Field(
        column_name="Pistol Squat Waga", attribute="pistol_squat_weight"
    )
    pistol_squat_body_percent = fields.Field(
        column_name="Pistol Squat % Wagi Ciała", attribute="pistol_squat_body_percent"
    )
    pistol_squat_position = fields.Field(
        column_name="Miejsce Pistol Squat", attribute="pistol_squat_position"
    )

    overall_points = fields.Field(
        column_name="Punkty Ogółem", attribute="overall_points"
    )
    overall_position = fields.Field(
        column_name="Miejsce Ogółem", attribute="overall_position"
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
            "snatch_position",
            "tgu_weight",
            "tgu_body_percent",
            "tgu_position",
            "see_saw_press_weight_left",
            "see_saw_press_weight_right",
            "see_saw_press_body_percent_left",
            "see_saw_press_body_percent_right",
            "see_saw_press_position",
            "kb_squat_weight",
            "kb_squat_body_percent",
            "kb_squat_position",
            "pistol_squat_weight",
            "pistol_squat_body_percent",
            "pistol_squat_position",
            "overall_points",
            "overall_position",
            "tiebreak",
        )
        export_order = fields

    def dehydrate_snatch_results(self, player):
        result = (
            player.snatch_results() if player.snatch_results() is not None else "N/A"
        )
        print(f"Exporting Snatch Results for {player}: {result}")
        return result

    def dehydrate_snatch_position(self, player):
        snatch_result = player.snatchresult_set.first()
        position = snatch_result.position if snatch_result else "N/A"
        print(f"Exporting Snatch Position for {player}: {position}")
        return position

    def dehydrate_tgu_body_percent(self, player):
        result = (
            f"{player.tgu_body_percent_weight():.2f}%"
            if player.tgu_body_percent_weight() is not None
            else "N/A"
        )
        print(f"Exporting TGU Body Percent for {player}: {result}")
        return result

    def dehydrate_tgu_position(self, player):
        tgu_result = player.tguresult_set.first()
        position = tgu_result.position if tgu_result else "N/A"
        print(f"Exporting TGU Position for {player}: {position}")
        return position

    def dehydrate_see_saw_press_body_percent_left(self, player):
        result = (
            f"{player.see_saw_press_body_percent_weight_left():.2f}%"
            if player.see_saw_press_body_percent_weight_left() is not None
            else "N/A"
        )
        print(f"Exporting See Saw Press Body Percent (Left) for {player}: {result}")
        return result

    def dehydrate_see_saw_press_body_percent_right(self, player):
        result = (
            f"{player.see_saw_press_body_percent_weight_right():.2f}%"
            if player.see_saw_press_body_percent_weight_right() is not None
            else "N/A"
        )
        print(f"Exporting See Saw Press Body Percent (Right) for {player}: {result}")
        return result

    def dehydrate_see_saw_press_position(self, player):
        see_saw_result = player.seesawpressresult_set.first()
        position = see_saw_result.position if see_saw_result else "N/A"
        print(f"Exporting See Saw Press Position for {player}: {position}")
        return position

    def dehydrate_kb_squat_body_percent(self, player):
        result = (
            f"{player.kb_squat_body_percent_weight():.2f}%"
            if player.kb_squat_body_percent_weight() is not None
            else "N/A"
        )
        print(f"Exporting KB Squat Body Percent for {player}: {result}")
        return result

    def dehydrate_kb_squat_position(self, player):
        kb_squat_result = player.kbsquatresult_set.first()
        position = kb_squat_result.position if kb_squat_result else "N/A"
        print(f"Exporting KB Squat Position for {player}: {position}")
        return position

    def dehydrate_pistol_squat_weight(self, player):
        result = player.get_max_pistol_squat_weight()
        print(f"Exporting Pistol Squat Weight for {player}: {result}")
        return result

    def dehydrate_pistol_squat_body_percent(self, player):
        weight = player.get_max_pistol_squat_weight()
        result = f"{(weight / player.weight * 100):.2f}%" if player.weight else "N/A"
        print(f"Exporting Pistol Squat Body Percent for {player}: {result}")
        return result

    def dehydrate_pistol_squat_position(self, player):
        pistol_squat_result = player.pistolsquatresult_set.first()
        position = pistol_squat_result.position if pistol_squat_result else "N/A"
        print(f"Exporting Pistol Squat Position for {player}: {position}")
        return position

    def dehydrate_overall_points(self, player):
        overall_result = OverallResult.objects.filter(player=player).first()
        points = overall_result.total_points if overall_result else "N/A"
        print(f"Exporting Overall Points for {player}: {points}")
        return points

    def dehydrate_overall_position(self, player):
        overall_result = OverallResult.objects.filter(player=player).first()
        position = overall_result.final_position if overall_result else "N/A"
        print(f"Exporting Overall Position for {player}: {position}")
        return position
