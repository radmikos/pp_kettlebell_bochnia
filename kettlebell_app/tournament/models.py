from django.db import models


class SportClub(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class WeightCategory(models.Model):
    name = models.CharField(max_length=50)
    weight = models.FloatField()

    def __str__(self):
        return f"{self.name} ({self.weight} kg)"


class Level(models.Model):
    name = models.CharField(max_length=50)  # np. "Amator", "Pro"

    def __str__(self):
        return self.name


class Player(models.Model):
    name = models.CharField(max_length=50)
    surname = models.CharField(max_length=50)
    weight = models.FloatField()
    club = models.ForeignKey(SportClub, on_delete=models.CASCADE)
    category = models.ForeignKey(WeightCategory, on_delete=models.CASCADE)
    level = models.ForeignKey(Level, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} {self.surname}"


class SnatchResults(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    sum_weight = models.FloatField()

    def __str__(self):
        return f"{self.player} - Snatch: {self.sum_weight} kg"


class TGUResults(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    weight = models.FloatField()

    def body_percent_weight(self):
        return (self.weight / self.player.weight) * 100

    def __str__(self):
        return f"{self.player} - TGU: {self.weight} kg ({self.body_percent_weight():.2f}%)"


class SeeSawPressWeight(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    weight = models.FloatField()

    def body_percent_weight(self):
        return (self.weight / self.player.weight) * 100

    def __str__(self):
        return f"{self.player} - See Saw Press: {self.weight} kg ({self.body_percent_weight():.2f}%)"


class Results2xKBSQAD(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    weight = models.FloatField()

    def body_percent_weight(self):
        return (self.weight / self.player.weight) * 100

    def __str__(self):
        return f"{self.player} - 2xKBSQAD: {self.weight} kg ({self.body_percent_weight():.2f}%)"
