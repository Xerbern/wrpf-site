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
        M_59 = "59", _("59 kg")
        M_66 = "66", _("66 kg")
        M_74 = "74", _("74 kg")
        M_83 = "83", _("83 kg")
        M_93 = "93", _("93 kg")
        M_105 = "105", _("105 kg")
        M_120 = "120", _("120 kg")
        M_120_PLUS = "120+", _("120+ kg")

        W_47 = "47", _("47 kg")
        W_52 = "52", _("52 kg")
        W_57 = "57", _("57 kg")
        W_63 = "63", _("63 kg")
        W_69 = "69", _("69 kg")
        W_76 = "76", _("76 kg")
        W_84 = "84", _("84 kg")
        W_84_PLUS = "84+", _("84+ kg")

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
    weight_class = models.CharField(
        max_length=10,
        choices=WeightClassChoices.choices,
    )
    is_tested = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("meet", "email")

    def __str__(self):
        return f"{self.full_name} - {self.meet.name}"
