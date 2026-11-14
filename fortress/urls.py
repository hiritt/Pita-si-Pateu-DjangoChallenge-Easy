from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path
from units import views

urlpatterns = [
    path("", lambda request: redirect("unit_all"), name="home"),
    path("admin/", admin.site.urls),
    path("unit", views.add_unit, name="unit"),
    path("unit/", views.add_unit, name="unit_slash"),
    path("unit/all", views.all_units, name="unit_all"),
    path("unit/all/", views.all_units, name="unit_all_slash"),
    path("unit/<int:unit_id>", views.unit_detail, name="unit_detail"),
    path("unit/<int:unit_id>/", views.unit_detail, name="unit_detail_slash"),
    path("unit/<int:unit_id>/heal", views.heal_unit, name="unit_heal"),
    path("unit/<int:unit_id>/heal/", views.heal_unit, name="unit_heal_slash"),
    path("fight/simulate", views.simulate, name="simulate"),
    path("fight/simulate/", views.simulate, name="simulate_slash"),
]
