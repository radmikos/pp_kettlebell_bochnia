from django import forms


class StationForm(forms.Form):
    category = forms.ChoiceField(
        choices=[
            ("amator_kobiety_do_65kg", "Amator Kobiety do 65kg"),
            ("amator_kobiety_powyzej_65kg", "Amator Kobiety powyżej 65kg"),
            # Add more categories as needed
        ]
    )
    stations = forms.IntegerField(min_value=1, label="Number of Stations")
