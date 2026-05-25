from django.core.mail import EmailMultiAlternatives, send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.db import IntegrityError
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from .models import Meet, Registration
from .forms import RegistrationForm

import base64
from io import BytesIO

import qrcode

def meet_list(request):
    status = request.GET.get("status")

    meets = Meet.objects.all().order_by("date")

    if status == "open":
        meets = meets.filter(registration_open=True)

    elif status == "closed":
        meets = meets.filter(registration_open=False)

    context = {
        "meets": meets
    }

    if request.headers.get("HX-Request"):
        return render(request, "meets/partials/meet_list.html", context)

    return render(request, "meets/meet_list.html", context)

def meet_details(request, pk):
    meet = get_object_or_404(Meet, pk=pk)
    form = RegistrationForm()
    return render(request, "meets/meet_details.html", {"meet": meet, "form": form})

def register_success(request, pk, registration_id):
    meet = get_object_or_404(Meet, pk=pk)
    registration = get_object_or_404(
        Registration,
        pk=registration_id,
        meet=meet,
    )
    
    # so we don't access the successful page directly after registration
    if request.session.get("last_registration_id") != registration.pk:
        return redirect("meet_details", pk=meet.pk)

    qr_payload = request.build_absolute_uri(
        reverse("registration_verify", args=[registration.id])
    )
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=4,
        border=2,
    )
    qr.add_data(qr_payload)
    qr.make(fit=True)

    qr_img = qr.make_image(fill_color="black", back_color="white")

    buffer = BytesIO()
    qr_img.save(buffer, format="PNG")
    qr_code_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

    # deletes the last_reg_id after first navigation
    request.session.pop("last_registration_id", None)

    return render(
        request,
        "meets/register_success.html",
        {
            "meet": meet,
            "registration": registration,
            "qr_code_base64": qr_code_base64,
            "qr_payload": qr_payload,
        },
    )

@require_http_methods(["POST"])
def meet_register(request, pk):
    meet = get_object_or_404(Meet, pk=pk)
    form = RegistrationForm(request.POST)

    if not meet.registration_open:
        messages.error(request, _("Registration is closed."))
        return redirect("meet_details", pk=pk)

    if not form.is_valid():
        return render(
            request,
            "meets/meet_details.html",
            {
                "meet": meet,
                "form": form,
            },
            status=400,
        )

    try:
        registration = form.save(commit=False)
        registration.meet = meet
        registration.save()
    except IntegrityError:
        form.add_error("email", _("This email is already registered for this meet."))
        return render(
            request,
            "meets/meet_details.html",
            {
                "meet": meet,
                "form": form,
            },
            status=400,
        )

    try:
        subject = _("WRPF Romania Registration Confirmation - %(meet)s") % {
            "meet": meet.name
        }

        verification_url = request.build_absolute_uri(
            reverse("registration_verify", args=[registration.id])
        )

        context = {
            "meet": meet,
            "registration": registration,
            "verification_url": verification_url,
        }

        html_content = render_to_string(
            "emails/registration_confirmation.html",
            context,
        )
        text_content = strip_tags(html_content)

        email_message = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=None,
            to=[registration.email],
        )
        email_message.attach_alternative(html_content, "text/html")
        email_message.send()

    except Exception as e:
        print("EMAIL ERROR:", repr(e))
        messages.warning(
            request,
            _("Registration was saved, but the confirmation email could not be sent.")
        )

    # Idea for the future, send emails to the admin on new registration for specific meets
    # admin_subject = f"New registration - {meet.name}"
    # admin_message = (
    #     f"New registration received:\n\n"
    #     f"Name: {registration.full_name}\n"
    #     f"Email: {registration.email}\n"
    #     f"Sex: {registration.sex}\n"
    #     f"Weight class: {registration.weight_class}\n"
    #     f"Tested: {'Yes' if registration.is_tested else 'No'}\n\n"
    #     f"Meet: {meet.name}\n"
    #     f"Date: {meet.date}"
    # )
    # send_mail(
    #     subject=admin_subject,
    #     message=admin_message,
    #     from_email=None,
    #     recipient_list=["nezko45@gmail.com"],
    #     fail_silently=False,
    # )

    request.session["last_registration_id"] = registration.pk
    return redirect("register_success", pk=meet.pk, registration_id=registration.pk)


def registration_verify(request, registration_id):
    registration = get_object_or_404(
        Registration.objects.select_related("meet"),
        pk=registration_id,
    )
    meet = registration.meet

    context = {
        "registration": registration,
        "meet": meet,
        "verified_at": timezone.now(),
    }
    return render(request, "meets/registration_verify.html", context)