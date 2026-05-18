from django.urls import path
from . import views

urlpatterns = [
    # Clean, top-level URLs that both hit the same view:
    path('rulebook/', views.show_pdf, {'slug': 'rulebook'}, name='rulebook'),
    path('banned-substances/', views.show_pdf, {'slug': 'banned_substances'}, name='banned_substances'),
    path('drug-testing-policies/', views.show_pdf, {'slug': 'drug-testing-policies'}, name='drug_testing_policies'),
]