from import_export import resources, fields
from import_export.widgets import ManyToManyWidget, ForeignKeyWidget
from .models import Player, SportClub, Category

class PlayerResource(resources.ModelResource):
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
    see_saw_press_body_percent = fields.Field(column_name='See Saw Press % Wagi Ciała', attribute='see_saw_press_body_percent_weight')
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