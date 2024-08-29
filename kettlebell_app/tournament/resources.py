from import_export import resources, fields
from import_export.widgets import ManyToManyWidget, ForeignKeyWidget
from django.db import models
from .models import Player, SportClub, Category

class CustomForeignKeyWidget(ForeignKeyWidget):
    def clean(self, value, row=None, *args, **kwargs):
        if value:
            try:
                return self.get_queryset(value, row, *args, **kwargs).get(**{self.field: value})
            except self.model.DoesNotExist:
                return self.model.objects.create(**{self.field: value})
            except self.model.MultipleObjectsReturned:
                return self.get_queryset(value, row, *args, **kwargs).first()
        return None

class PlayerImportResource(resources.ModelResource):
    name = fields.Field(column_name='Imię', attribute='name')
    surname = fields.Field(column_name='Nazwisko', attribute='surname')
    club = fields.Field(
        column_name='Klub',
        attribute='club',
        widget=CustomForeignKeyWidget(SportClub, 'name')
    )
    categories = fields.Field(
        column_name='Kategoria',
        attribute='categories',
        widget=ManyToManyWidget(Category, field='name', separator=', ')
    )

    class Meta:
        model = Player
        fields = ('name', 'surname', 'club', 'categories')
        import_id_fields = ('name', 'surname', 'club')

    def before_import_row(self, row, **kwargs):
        # Upewnij się, że wszystkie kategorie istnieją
        for category_name in row['Kategoria'].split(', '):
            Category.objects.get_or_create(name=category_name.strip())

    def import_obj(self, obj, data, dry_run, **kwargs):
        for field in self.get_fields():
            if isinstance(field, fields.Field) and field.attribute:
                if field.column_name == 'Kategoria':
                    # Obsługa wielu kategorii
                    categories = [category.strip() for category in data['Kategoria'].split(', ')]
                    category_objects = [Category.objects.get(name=cat) for cat in categories]
                    if not dry_run:
                        obj.categories.set(category_objects)
                else:
                    self.import_field(field, obj, data)

        if not dry_run:
            obj.save()

class PlayerExportResource(resources.ModelResource):
    club = fields.Field(
        column_name='Klub',
        attribute='club',
        widget=ForeignKeyWidget(SportClub, 'name')
    )
    categories = fields.Field(
        column_name='Kategoria',
        attribute='categories',
        widget=ManyToManyWidget(Category, field='name', separator=', ')
    )
    snatch_results = fields.Field(column_name='Wyniki Rwania', attribute='snatch_results')
    tgu_body_percent = fields.Field(column_name='TGU % Wagi Ciała', attribute='tgu_body_percent_weight')
    see_saw_press_body_percent = fields.Field(column_name='See Saw Press % Wagi Ciała',
                                              attribute='see_saw_press_body_percent_weight')
    kb_squat_body_percent = fields.Field(column_name='KB Squat % Wagi Ciała', attribute='kb_squat_body_percent_weight')

    class Meta:
        model = Player
        fields = ('name', 'surname', 'weight', 'club', 'categories',
                  'snatch_kettlebell_weight', 'snatch_repetitions', 'snatch_results',
                  'tgu_weight', 'tgu_body_percent',
                  'see_saw_press_weight', 'see_saw_press_body_percent',
                  'kb_squat_weight', 'kb_squat_body_percent')
        export_order = fields

    def dehydrate_snatch_results(self, player):
        return player.snatch_results() if player.snatch_results() is not None else 'N/A'

    def dehydrate_tgu_body_percent(self, player):
        return f"{player.tgu_body_percent_weight():.2f}%" if player.tgu_body_percent_weight() is not None else 'N/A'

    def dehydrate_see_saw_press_body_percent(self, player):
        return f"{player.see_saw_press_body_percent_weight():.2f}%" if player.see_saw_press_body_percent_weight() is not None else 'N/A'

    def dehydrate_kb_squat_body_percent(self, player):
        return f"{player.kb_squat_body_percent_weight():.2f}%" if player.kb_squat_body_percent_weight() is not None else 'N/A'