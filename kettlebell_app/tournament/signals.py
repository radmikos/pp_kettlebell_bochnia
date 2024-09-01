# results/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import SnatchResult, TGUResult, SeeSawPressResult, KBSquatResult, Player

@receiver(post_save, sender=SnatchResult)
@receiver(post_save, sender=TGUResult)
@receiver(post_save, sender=SeeSawPressResult)
@receiver(post_save, sender=KBSquatResult)
def update_player_results(sender, instance, **kwargs):
    player = instance.player
    if isinstance(instance, SnatchResult):
        player.snatch_kettlebell_weight = instance.result
        player.snatch_repetitions = instance.position
    elif isinstance(instance, TGUResult):
        player.tgu_weight = instance.result
    elif isinstance(instance, SeeSawPressResult):
        player.see_saw_press_weight = instance.result
    elif isinstance(instance, KBSquatResult):
        player.kb_squat_weight = instance.result
    player.save()
    # Optionally update or create overall results
    # This will depend on your calculation logic and when you want to do this
