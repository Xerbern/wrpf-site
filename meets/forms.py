from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Registration


MEN_WEIGHT_CLASSES = [
    (Registration.WeightClassChoices.M_52, _("52 kg")),
    (Registration.WeightClassChoices.M_56, _("56 kg")),
    (Registration.WeightClassChoices.M_60, _("60 kg")),
    (Registration.WeightClassChoices.M_67_5, _("67.5 kg")),
    (Registration.WeightClassChoices.M_75, _("75 kg")),
    (Registration.WeightClassChoices.M_82_5, _("82.5 kg")),
    (Registration.WeightClassChoices.M_90, _("90 kg")),
    (Registration.WeightClassChoices.M_100, _("100 kg")),
    (Registration.WeightClassChoices.M_110, _("110 kg")),
    (Registration.WeightClassChoices.M_125, _("125 kg")),
    (Registration.WeightClassChoices.M_140, _("140 kg")),
    (Registration.WeightClassChoices.M_140_PLUS, _("140+ kg")),
]

WOMEN_WEIGHT_CLASSES = [
    (Registration.WeightClassChoices.W_44, _("44 kg")),
    (Registration.WeightClassChoices.W_48, _("48 kg")),
    (Registration.WeightClassChoices.W_52, _("52 kg")),
    (Registration.WeightClassChoices.W_56, _("56 kg")),
    (Registration.WeightClassChoices.W_60, _("60 kg")),
    (Registration.WeightClassChoices.W_67_5, _("67.5 kg")),
    (Registration.WeightClassChoices.W_75, _("75 kg")),
    (Registration.WeightClassChoices.W_82_5, _("82.5 kg")),
    (Registration.WeightClassChoices.W_90, _("90 kg")),
    (Registration.WeightClassChoices.W_90_PLUS, _("90+ kg")),
]


class RegistrationForm(forms.ModelForm):
    honeypot = forms.CharField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = Registration
        fields = [
            "full_name",
            "email",
            "sex",
            "date_of_birth",
            "weight_class",
            "disciplines",
            "is_tested",
        ]
        labels = {
            "full_name": _("Full name"),
            "email": _("Email"),
            "sex": _("Division"),
            "date_of_birth": _("Date of birth"),
            "weight_class": _("Weight class"),
            "disciplines": _("Disciplines"),
            "is_tested": _("Anti-doping tested"),
        }
        widgets = {
            "full_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "sex": forms.Select(attrs={"class": "form-select"}),
            "date_of_birth": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),
            "weight_class": forms.Select(attrs={"class": "form-select"}),
            "disciplines": forms.HiddenInput(attrs={"id": "id_disciplines"}),
            "is_tested": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["sex"].choices = [
            ("", _("Select division")),
            *Registration.SexChoices.choices,
        ]
        self.fields["weight_class"].choices = [
            ("", _("Select weight class")),
            *Registration.WeightClassChoices.choices,
        ]

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        return email

    def clean(self):
        cleaned_data = super().clean()

        if cleaned_data.get("honeypot"):
            raise forms.ValidationError("Invalid submission.")

        sex = cleaned_data.get("sex")
        weight_class = cleaned_data.get("weight_class")

        men_weight_classes = {choice[0] for choice in MEN_WEIGHT_CLASSES}
        women_weight_classes = {choice[0] for choice in WOMEN_WEIGHT_CLASSES}

        if sex == Registration.SexChoices.MEN and weight_class not in men_weight_classes:
            self.add_error("weight_class", _("Invalid weight class for the selected division."))

        if sex == Registration.SexChoices.WOMEN and weight_class not in women_weight_classes:
            self.add_error("weight_class", _("Invalid weight class for the selected division."))

        disciplines = cleaned_data.get("disciplines") or []

        valid_disciplines = {
            choice[0] for choice in Registration.DisciplineChoices.choices
        }

        if not disciplines:
            self.add_error("disciplines", _("Please select at least one discipline."))

        invalid_disciplines = [
            discipline for discipline in disciplines
            if discipline not in valid_disciplines
        ]

        if invalid_disciplines:
            self.add_error("disciplines", _("Invalid discipline selected."))

        return cleaned_data