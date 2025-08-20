from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("export/<int:product_id>/", views.export_excel, name="export_excel"),
]
