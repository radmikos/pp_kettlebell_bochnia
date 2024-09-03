from django.db import migrations


def forward_func(apps, schema_editor):
    OverallResult = apps.get_model("tournament", "OverallResult")
    for result in OverallResult.objects.all():
        result.snatch_points = result.snatch_points or 0
        result.tgu_points = result.tgu_points or 0
        result.see_saw_press_points = result.see_saw_press_points or 0
        result.kb_squat_points = result.kb_squat_points or 0
        result.pistol_squat_points = result.pistol_squat_points or 0
        result.tiebreak_points = result.tiebreak_points or 0
        result.total_points = result.total_points or 0
        result.save()


class Migration(migrations.Migration):

    dependencies = [
        (
            "tournament",
            "0005_overallresult_pistol_squat_points_and_more",
        ),  # replace with the name of your last migration
    ]

    operations = [
        migrations.RunPython(forward_func),
    ]
