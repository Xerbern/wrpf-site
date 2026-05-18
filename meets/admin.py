from django.contrib import admin
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

    @admin.display(description=("Registrations"))
    def registration_count(self, obj):
        return obj.registrations.count()

admin.site.register(Registration)