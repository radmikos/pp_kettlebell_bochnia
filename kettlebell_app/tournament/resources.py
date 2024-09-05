from django.core.exceptions import MultipleObjectsReturned  # Dodane importy
from django.core.exceptions import ValidationError
from django.db.models import Q
from import_export import fields, resources
from import_export.widgets import ForeignKeyWidget, ManyToManyWidget

from .models import Category, Player, SportClub


class CustomForeignKeyWidget(ForeignKeyWidget):
    def clean(self, value, row=None, *args, **kwargs):
        if value:
            try:
                return (
                    self.get_queryset(value, row, *args, **kwargs)
                    .filter(**{self.field: value})
                    .first()
                )
            except self.model.DoesNotExist:
                return self.model.objects.create(**{self.field: value})
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

    class Meta:
        model = Player
        fields = ("name", "surname", "club", "categories")
        import_id_fields = ["name", "surname", "club"]

    def before_import_row(self, row, **kwargs):
        club_name = row.get("Klub", "")
        name = row.get("Imię", "")
        surname = row.get("Nazwisko", "")
        categories = row.get("Kategoria", "").split(", ")

        try:
            club, _ = SportClub.objects.get_or_create(name=club_name)
            player, created = Player.objects.get_or_create(
                name=name, surname=surname, club=club, defaults={"club": club}
            )

            for category_name in categories:
                category, _ = Category.objects.get_or_create(name=category_name)
                player.categories.add(category)

            # Ustawiamy dane w wierszu, aby były użyte przez import_row
            row["name"] = name
            row["surname"] = surname
            row["club"] = club_name
            row["categories"] = ", ".join(categories)

        except ValidationError:
            # Obsłuż błąd walidacji, jeśli to konieczne
            pass

    def import_row(self, row, instance_loader, **kwargs):
        try:
            # Pobieranie pól z wiersza
            params = {}
            for field in self.get_fields():
                field_name = self.get_field_name(field)
                params[field_name] = field.clean(row)

            # Sprawdzenie, czy zawodnik istnieje
            existing_player = Player.objects.filter(
                Q(name=params["name"])
                & Q(surname=params["surname"])
                & Q(club__name=params["club"])
            ).first()

            # Jeśli zawodnik istnieje
            if existing_player:
                # Wywołujemy standardowy mechanizm importowania, aby uzyskać wynik
                result = super(PlayerImportResource, self).import_row(
                    row, instance_loader, **kwargs
                )

                # Aktualizujemy kategorie po wywołaniu `import_row`
                new_categories = params["categories"]
                existing_categories = set(
                    existing_player.categories.values_list("name", flat=True)
                )

                for category in new_categories:
                    if category not in existing_categories:
                        category_instance, _ = Category.objects.get_or_create(
                            name=category
                        )
                        existing_player.categories.add(category_instance)

                # Zwracamy wynik, aby nie powodować błędów w bibliotece import-export
                return result
            else:
                # Jeśli zawodnik nie istnieje, wykonaj normalne importowanie
                return super(PlayerImportResource, self).import_row(
                    row, instance_loader, **kwargs
                )

        except Exception as e:
            # Obsługa błędów
            print(f"Error during import: {str(e)}")
            return super(PlayerImportResource, self).import_row(
                row, instance_loader, **kwargs
            )


from django.db.models import F, Max
from import_export import fields, resources
from import_export.widgets import ForeignKeyWidget, ManyToManyWidget

from .models import Category, Player, SportClub


class PlayerExportResource(resources.ModelResource):
    club = fields.Field(
        column_name="Klub", attribute="club", widget=ForeignKeyWidget(SportClub, "name")
    )
    categories = fields.Field(
        column_name="Kategorie",
        attribute="categories",
        widget=ManyToManyWidget(Category, field="name", separator=", "),
    )

    snatch_result = fields.Field(column_name="Snatch Wynik", attribute="snatch_results")
    snatch_position = fields.Field(column_name="Snatch Pozycja")

    tgu_max = fields.Field(column_name="TGU Max")
    tgu_bw_percentage = fields.Field(column_name="TGU %BW")
    tgu_position = fields.Field(column_name="TGU Pozycja")

    see_saw_press_max_left = fields.Field(column_name="See Saw Press Max Lewy")
    see_saw_press_max_right = fields.Field(column_name="See Saw Press Max Prawy")
    see_saw_press_position = fields.Field(column_name="See Saw Press Pozycja")

    kb_squat_max = fields.Field(column_name="KB Squat Max")
    kb_squat_position = fields.Field(column_name="KB Squat Pozycja")

    pistol_squat_max = fields.Field(column_name="Pistol Squat Max")
    pistol_squat_position = fields.Field(column_name="Pistol Squat Pozycja")

    total_points = fields.Field(column_name="Suma Punktów")
    final_position = fields.Field(column_name="Pozycja Końcowa")
    final_score = fields.Field(column_name="Ostateczny Wynik")

    class Meta:
        model = Player
        fields = (
            "id",
            "name",
            "surname",
            "weight",
            "club",
            "categories",
            "snatch_kettlebell_weight",
            "snatch_repetitions",
            "snatch_result",
            "snatch_position",
            "tgu_weight_1",
            "tgu_weight_2",
            "tgu_weight_3",
            "tgu_max",
            "tgu_bw_percentage",
            "tgu_position",
            "see_saw_press_weight_left_1",
            "see_saw_press_weight_right_1",
            "see_saw_press_weight_left_2",
            "see_saw_press_weight_right_2",
            "see_saw_press_weight_left_3",
            "see_saw_press_weight_right_3",
            "see_saw_press_max_left",
            "see_saw_press_max_right",
            "see_saw_press_position",
            "kb_squat_weight_left_1",
            "kb_squat_weight_right_1",
            "kb_squat_weight_left_2",
            "kb_squat_weight_right_2",
            "kb_squat_weight_left_3",
            "kb_squat_weight_right_3",
            "kb_squat_max",
            "kb_squat_position",
            "pistol_squat_weight_1",
            "pistol_squat_weight_2",
            "pistol_squat_weight_3",
            "pistol_squat_max",
            "pistol_squat_position",
            "tiebreak",
            "total_points",
            "final_position",
            "final_score",
        )
        export_order = fields

    def get_queryset(self):
        return (
            Player.objects.annotate(
                tgu_max=Max(F("tgu_weight_1"), F("tgu_weight_2"), F("tgu_weight_3")),
                pistol_squat_max=Max(
                    F("pistol_squat_weight_1"),
                    F("pistol_squat_weight_2"),
                    F("pistol_squat_weight_3"),
                ),
            )
            .select_related("club")
            .prefetch_related(
                "categories",
                "snatchresult_set",
                "tguresult_set",
                "seesawpressresult_set",
                "kbsquatresult_set",
                "pistolsquatresult_set",
                "overallresult_set",
            )
        )

    def dehydrate_snatch_position(self, player):
        return (
            player.snatchresult_set.first().position
            if player.snatchresult_set.exists()
            else None
        )

    def dehydrate_tgu_bw_percentage(self, player):
        return (player.tgu_max / player.weight * 100) if player.weight else None

    def dehydrate_tgu_position(self, player):
        return (
            player.tguresult_set.first().position
            if player.tguresult_set.exists()
            else None
        )

    def dehydrate_see_saw_press_max_left(self, player):
        result = player.seesawpressresult_set.first()
        return (
            max(
                result.result_left_1 or 0,
                result.result_left_2 or 0,
                result.result_left_3 or 0,
            )
            if result
            else None
        )

    def dehydrate_see_saw_press_max_right(self, player):
        result = player.seesawpressresult_set.first()
        return (
            max(
                result.result_right_1 or 0,
                result.result_right_2 or 0,
                result.result_right_3 or 0,
            )
            if result
            else None
        )

    def dehydrate_see_saw_press_position(self, player):
        return (
            player.seesawpressresult_set.first().position
            if player.seesawpressresult_set.exists()
            else None
        )

    def dehydrate_kb_squat_max(self, player):
        result = player.kbsquatresult_set.first()
        return result.get_max_result() if result else None

    def dehydrate_kb_squat_position(self, player):
        return (
            player.kbsquatresult_set.first().position
            if player.kbsquatresult_set.exists()
            else None
        )

    def dehydrate_pistol_squat_position(self, player):
        return (
            player.pistolsquatresult_set.first().position
            if player.pistolsquatresult_set.exists()
            else None
        )

    def dehydrate_total_points(self, player):
        overall = player.overallresult_set.first()
        return overall.total_points if overall else None

    def dehydrate_final_position(self, player):
        overall = player.overallresult_set.first()
        return overall.final_position if overall else None

    def dehydrate_final_score(self, player):
        overall = player.overallresult_set.first()
        if overall:
            return (
                overall.total_points - 0.5 if player.tiebreak else overall.total_points
            )
        return None
