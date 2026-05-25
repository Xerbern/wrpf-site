from django.db import models
from django.utils.translation import gettext_lazy as _

# Meet
class Meet(models.Model):
    name = models.CharField(_("Name"), max_length=200)
    date = models.DateField(_("Date"))
    location = models.CharField(_("Location"), max_length=200)
    registration_open = models.BooleanField(_("Registration open"), default=True)


# Registration
class Registration(models.Model):
    class SexChoices(models.TextChoices):
        MEN = "men", _("Men")
        WOMEN = "women", _("Women")

    class WeightClassChoices(models.TextChoices):
        M_52 = "men_52", _("52 kg")
        M_56 = "men_56", _("56 kg")
        M_60 = "men_60", _("60 kg")
        M_67_5 = "men_67.5", _("67.5 kg")
        M_75 = "men_75", _("75 kg")
        M_82_5 = "men_82.5", _("82.5 kg")
        M_90 = "men_90", _("90 kg")
        M_100 = "men_100", _("100 kg")
        M_110 = "men_110", _("110 kg")
        M_125 = "men_125", _("125 kg")
        M_140 = "men_140", _("140 kg")
        M_140_PLUS = "men_140+", _("140+ kg")

        W_44 = "women_44", _("44 kg")
        W_48 = "women_48", _("48 kg")
        W_52 = "women_52", _("52 kg")
        W_56 = "women_56", _("56 kg")
        W_60 = "women_60", _("60 kg")
        W_67_5 = "women_67.5", _("67.5 kg")
        W_75 = "women_75", _("75 kg")
        W_82_5 = "women_82.5", _("82.5 kg")
        W_90 = "women_90", _("90 kg")
        W_90_PLUS = "women_90+", _("90+ kg")

    class DisciplineChoices(models.TextChoices):
        RAW_POWERLIFTING = "raw_powerlifting", _("Raw Powerlifting")
        CLASSIC_POWERLIFTING = "classic_powerlifting", _("Classic Powerlifting")
        SQUAT = "squat", _("Squat")
        BENCH_PRESS = "bench_press", _("Bench Press")
        DEADLIFT = "deadlift", _("Deadlift")

    meet = models.ForeignKey(
        Meet,
        on_delete=models.CASCADE,
        related_name="registrations",
    )
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    sex = models.CharField(
        max_length=10,
        choices=SexChoices.choices,
    )
    date_of_birth = models.DateField(
        _("Date of birth"),
        null=True,
        blank=True,
    )
    weight_class = models.CharField(
        max_length=10,
        choices=WeightClassChoices.choices,
    )
    discipline = models.CharField(
        _("Discipline"),
        max_length=30,
        choices=DisciplineChoices.choices,
        default=DisciplineChoices.RAW_POWERLIFTING,
    )
    is_tested = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("meet", "email")

    def __str__(self):
        return f"{self.full_name} - {self.meet.name}"
