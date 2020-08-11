from django.conf.urls import url
from django.urls import path

from . import views

urlpatterns = [
    path('', views.uncertainty_home, name='uncertainty_home'),
    path('variant/<int:variant>', views.uncertainty_variant, name='uncertainty_variant')
]
