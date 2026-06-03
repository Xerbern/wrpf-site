import csv

from django.contrib import admin
from django.http import HttpResponse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import Meet, Registration


admin.site.site_header = "WRPF Romania Admin"
admin.site.site_title = "WRPF RO Admin"
admin.site.index_title = "Federation Management"


@admin.register(Meet)
class MeetAdmin(admin.ModelAdmin):
    list_display = ("name", "date", "location", "registration_open", "registration_count")
    list_filter = ("registration_open", "date")
    search_fields = ("name", "location")
    ordering = ("date",)
    list_editable = ("registration_open",)

    @admin.display(description="Registrations")
    def registration_count(self, obj):
        return obj.registrations.count()


@admin.action(description=_("Export registrations to CSV"))
def export_registrations_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="wrpf_registrations.csv"'

    writer = csv.writer(response)
    writer.writerow([
        "Meet",
        "Full name",
        "Email",
        "Date of birth",
        "Sex",
        "Divisions",
        "Weight class",
        "disciplines",
        "Tested",
        "Paid",
        "Payment notes",
        "Created at",
    ])

    for registration in queryset.select_related("meet"):
        writer.writerow([
            registration.meet.name,
            registration.full_name,
            registration.email,
            registration.date_of_birth,
            registration.get_sex_display(),
            ", ".join(
                str(dict(Registration.DivisionChoices.choices).get(division, division))
                for division in registration.divisions
            ),
            registration.get_weight_class_display(),
            ", ".join(
                str(dict(Registration.DisciplineChoices.choices).get(discipline, discipline))
                for discipline in registration.disciplines
            ),
            "Yes" if registration.is_tested else "No",
            "Yes" if registration.paid else "No",
            registration.payment_notes,
            registration.created_at,
        ])

    return response


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):

    list_display = (
        "full_name",
        "meet",
        "email",
        "sex",
        "weight_class",
        "disciplines_display",
        "divisions_display",
        "is_tested",
        "paid_status",
        "created_at",
        "date_of_birth",
    )

    list_filter = (
        "meet",
        "sex",
        "disciplines",
        "is_tested",
        "paid",
        "created_at",
    )

    search_fields = (
        "full_name",
        "email",
        "meet__name",
    )

    readonly_fields = (
        "created_at",
    )

    ordering = ("-created_at",)

    list_per_page = 50

    actions = [export_registrations_csv]

    @admin.display(description=_("Payment"))
    def paid_status(self, obj):
        if obj.paid:
            return format_html(
                '<span style="color:#22c55e;font-weight:bold;">PLĂTIT</span>'
            )

        return format_html(
            '<span style="color:#ef4444;font-weight:bold;">NEPLĂTIT</span>'
        )

    fieldsets = (
        ("Detalii sportiv", {
            "fields": (
                "meet",
                "full_name",
                "email",
                "date_of_birth",
                "sex",
                "divisions",
                "weight_class",
                "disciplines",
                "is_tested",
            )
        }),
        ("Plată", {
            "fields": (
                "paid",
                "payment_notes",
            )
        }),
        ("Sistem", {
            "fields": (
                "created_at",
            )
        }),
    )

    @admin.display(description=_("Disciplines"))
    def disciplines_display(self, obj):
        discipline_labels = dict(Registration.DisciplineChoices.choices)

        return ", ".join(
            str(discipline_labels.get(discipline, discipline))
            for discipline in obj.disciplines
        )

    @admin.display(description=_("Divisions"))
    def divisions_display(self, obj):
        labels = dict(Registration.DivisionChoices.choices)

        return ", ".join(
            str(labels.get(division, division))
            for division in obj.divisions
        )