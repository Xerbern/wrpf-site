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
from django_ratelimit.decorators import ratelimit
from .models import Meet, Registration
from .forms import RegistrationForm
from project.settings import DEFAULT_FROM_EMAIL

import base64
from io import BytesIO

import qrcode

def get_disciplines_display(registration):
    discipline_labels = dict(Registration.DisciplineChoices.choices)

    return ", ".join(
        str(discipline_labels.get(discipline, discipline))
        for discipline in registration.disciplines
    )

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

    return render(
        request,
        "meets/meet_details.html",
        {
            "meet": meet,
            "form": form,
            "discipline_choices": Registration.DisciplineChoices.choices,
        },
    )

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

    disciplines_display = get_disciplines_display(registration)
    
    return render(
        request,
        "meets/register_success.html",
        {
            "meet": meet,
            "registration": registration,
            "qr_code_base64": qr_code_base64,
            "qr_payload": qr_payload,
            "disciplines_display": disciplines_display,
        },
    )

@ratelimit(key="ip", rate="5/h", method="POST", block=False)
def meet_register(request, pk):
    if getattr(request, "limited", False):
        messages.error(
            request,
            _("Too many registration attempts. Please try again later.")
        )
        return redirect("meet_details", pk=pk)
    
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
                "discipline_choices": Registration.DisciplineChoices.choices,
            },
            status=400,
        )

    try:
        registration = form.save(commit=False)
        registration.meet = meet
        registration.save()
        disciplines_display = get_disciplines_display(registration)
    except IntegrityError:
        form.add_error("email", _("This email is already registered for this meet."))
        return render(
            request,
            "meets/meet_details.html",
            {
                "meet": meet,
                "form": form,
                "discipline_choices": Registration.DisciplineChoices.choices,
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
            "disciplines_display": disciplines_display,
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

    try:
        discipline_labels = dict(Registration.DisciplineChoices.choices)
        disciplines_display = ", ".join(
            str(discipline_labels.get(discipline, discipline))
            for discipline in registration.disciplines
        )

        admin_subject = f"Înscriere nouă - {meet.name}"
        admin_message = (
            f"Înscriere nouă primită:\n\n"
            f"Nume: {registration.full_name}\n"
            f"Email: {registration.email}\n"
            f"Data nașterii: {registration.date_of_birth}\n"
            f"Divizie: {registration.get_sex_display()}\n"
            f"Categoria de greutate: {registration.get_weight_class_display()}\n"
            f"Discipline: {disciplines_display}\n"
            f"Testat antidoping: {'Da' if registration.is_tested else 'Nu'}\n\n"
            f"Competiție: {meet.name}\n"
            f"Data competiției: {meet.date}"
        )

        send_mail(
           subject=admin_subject,
           message=admin_message,
           from_email=None,
           recipient_list=[DEFAULT_FROM_EMAIL],
           fail_silently=False,
        )

    except Exception as e:
        print("ADMIN EMAIL ERROR:", repr(e))

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