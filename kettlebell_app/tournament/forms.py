from django import forms

from .models import Category


class StationForm(forms.Form):
    category = forms.ChoiceField(choices=[], label="Kategoria")
    stations = forms.IntegerField(min_value=1, label="Liczba stanowisk")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].choices = [
            (category.name, category.name.replace("_", " "))
            for category in Category.objects.all()
        ]
