from django.urls import path
from . import views

urlpatterns = [
    path("", views.meet_list, name="meet_list"),
    path("<int:pk>", views.meet_details, name="meet_details"),
    path("<int:pk>/register/", views.meet_register, name="meet_register"),
    path(
        "<int:pk>/register/success/<int:registration_id>/",
        views.register_success,
        name="register_success",
    ),
    path(
        "registrations/verify/<int:registration_id>/",
        views.registration_verify,
        name="registration_verify",
    ),
]