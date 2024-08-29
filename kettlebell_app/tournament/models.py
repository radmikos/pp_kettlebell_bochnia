from django.db import models


class SportClub(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Player(models.Model):
    name = models.CharField(max_length=50)
    surname = models.CharField(max_length=50)
    weight = models.FloatField()
    club = models.ForeignKey(SportClub, on_delete=models.CASCADE)
    categories = models.ManyToManyField(Category)

    snatch_kettlebell_weight = models.FloatField(null=True, blank=True)
    snatch_repetitions = models.IntegerField(null=True, blank=True)

    tgu_weight = models.FloatField(null=True, blank=True)
    see_saw_press_weight = models.FloatField(null=True, blank=True)
    kb_squat_weight = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} {self.surname}"

    def snatch_results(self):
        if self.snatch_kettlebell_weight and self.snatch_repetitions:
            return self.snatch_kettlebell_weight * self.snatch_repetitions
        return None

    def tgu_body_percent_weight(self):
        return (self.tgu_weight / self.weight) * 100 if self.tgu_weight else None

    def see_saw_press_body_percent_weight(self):
        return (self.see_saw_press_weight / self.weight) * 100 if self.see_saw_press_weight else None

    def kb_squat_body_percent_weight(self):
        return (self.kb_squat_weight / self.weight) * 100 if self.kb_squat_weight else None


class SnatchResult(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    result = models.FloatField()
    position = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.player} - Snatch: {self.result}"


class TGUResult(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    result = models.FloatField()
    position = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.player} - TGU: {self.result}"


class SeeSawPressResult(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    result = models.FloatField()
    position = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.player} - See Saw Press: {self.result}"


class KBSquatResult(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    result = models.FloatField()
    position = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.player} - KB Squat: {self.result}"


class OverallResult(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    snatch_points = models.IntegerField(default=0)
    tgu_points = models.IntegerField(default=0)
    see_saw_press_points = models.IntegerField(default=0)
    kb_squat_points = models.IntegerField(default=0)
    total_points = models.IntegerField(default=0)
    final_position = models.IntegerField(null=True, blank=True)

    def calculate_total_points(self):
        self.total_points = (
                self.snatch_points +
                self.tgu_points +
                self.see_saw_press_points +
                self.kb_squat_points
        )
        self.save()

    def __str__(self):
        return f"{self.player} - Total: {self.total_points}"
