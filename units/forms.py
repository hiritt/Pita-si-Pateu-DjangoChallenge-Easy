from django import forms
from .models import Unit


class UnitForm(forms.ModelForm):
    class Meta:
        model = Unit
        fields = [
            "name", "unit_type", "team", "health", "attack_points", "profile_image_link",
        ]
        labels = {
            "name": "Name", "unit_type": "Type", "team": "Team",
            "health": "Health", "attack_points": "AttackPoints",
            "profile_image_link": "ProfileImageLink",
        }
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "e.g. Aster"}),
            "health": forms.NumberInput(attrs={"min": 0, "max": 100, "step": 1}),
            "attack_points": forms.NumberInput(attrs={"min": 0, "max": 50, "step": 1}),
            "profile_image_link": forms.URLInput(
                attrs={"placeholder": "https://example.com/fighter.png"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # The challenge says Health defaults to 100, even when left blank.
        self.fields["health"].required = False
        self.fields["health"].initial = 100

    def clean_health(self):
        value = self.cleaned_data.get("health")
        return 100 if value is None else value

    def clean_name(self):
        name = self.cleaned_data["name"].strip()
        if not name:
            raise forms.ValidationError("Please enter a name.")
        return name

    def clean_profile_image_link(self):
        url = self.cleaned_data.get("profile_image_link", "")
        if url and not url.startswith(("http://", "https://")):
            raise forms.ValidationError("Enter a valid HTTP or HTTPS URL.")
        return url


class FightSelectionForm(forms.Form):
    fighter_one = forms.ModelChoiceField(
        queryset=Unit.objects.none(), label="First fighter",
        empty_label="Select fighter one",
    )
    fighter_two = forms.ModelChoiceField(
        queryset=Unit.objects.none(), label="Second fighter",
        empty_label="Select fighter two",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        eligible = Unit.objects.filter(health__gt=0).order_by("team", "name", "id")
        self.fields["fighter_one"].queryset = eligible
        self.fields["fighter_two"].queryset = eligible

    def clean(self):
        cleaned = super().clean()
        first = cleaned.get("fighter_one")
        second = cleaned.get("fighter_two")
        if first and second:
            if first.pk == second.pk:
                raise forms.ValidationError("Choose two different fighters.")
            if first.team == second.team:
                raise forms.ValidationError("The fighters must belong to different teams.")
        return cleaned
