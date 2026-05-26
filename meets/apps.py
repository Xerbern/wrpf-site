from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class MeetsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "meets"
    verbose_name = _("Competitions")