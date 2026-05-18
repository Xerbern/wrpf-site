from django.urls import path
from . import views

urlpatterns = [
    path("about/", views.about, name="about"),
    path("disciplines/", views.disciplines, name="disciplines"),
    path("equipment/", views.equipment, name="equipment"),
    path("age-categories/", views.age_categories, name="age_categories"),
    path("staff/", views.staff, name="staff"),
]