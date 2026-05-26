from django import template
from django.utils import timezone

from meets.models import Meet, Registration

register = template.Library()


@register.simple_tag
def admin_dashboard_stats():
    today = timezone.localdate()

    return {
        "total_registrations": Registration.objects.count(),
        "paid_registrations": Registration.objects.filter(paid=True).count(),
        "unpaid_registrations": Registration.objects.filter(paid=False).count(),
        "upcoming_meets": Meet.objects.filter(date__gte=today).count(),
        "open_meets": Meet.objects.filter(registration_open=True).count(),
        "latest_registrations": Registration.objects.select_related("meet").order_by("-created_at")[:5],
    }