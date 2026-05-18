from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Registration

MEN_WEIGHT_CLASSES = [
    (Registration.WeightClassChoices.M_59, _("59 kg")),
    (Registration.WeightClassChoices.M_66, _("66 kg")),
    (Registration.WeightClassChoices.M_74, _("74 kg")),
    (Registration.WeightClassChoices.M_83, _("83 kg")),
    (Registration.WeightClassChoices.M_93, _("93 kg")),
    (Registration.WeightClassChoices.M_105, _("105 kg")),
    (Registration.WeightClassChoices.M_120, _("120 kg")),
    (Registration.WeightClassChoices.M_120_PLUS, _("120+ kg")),
]

WOMEN_WEIGHT_CLASSES = [
    (Registration.WeightClassChoices.W_47, _("47 kg")),
    (Registration.WeightClassChoices.W_52, _("52 kg")),
    (Registration.WeightClassChoices.W_57, _("57 kg")),
    (Registration.WeightClassChoices.W_63, _("63 kg")),
    (Registration.WeightClassChoices.W_69, _("69 kg")),
    (Registration.WeightClassChoices.W_76, _("76 kg")),
    (Registration.WeightClassChoices.W_84, _("84 kg")),
    (Registration.WeightClassChoices.W_84_PLUS, _("84+ kg")),
]

class RegistrationForm(forms.ModelForm):
    honeypot = forms.CharField(required=False, widget=forms.HiddenInput)
    class Meta:
        model = Registration
        fields = ["full_name", "email", "sex", "weight_class", "is_tested"]
        labels = {
            "full_name": _("Full name"),
            "email": _("Email"),
            "sex": _("Division"),
            "weight_class": _("Weight class"),
            "is_tested": _("Tested division"),
        }
        widgets = {
            "full_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "sex": forms.Select(attrs={"class": "form-select"}),
            "weight_class": forms.Select(attrs={"class": "form-select"}),
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

        return cleaned_data