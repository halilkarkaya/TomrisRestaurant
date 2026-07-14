from django.urls import path

from . import views


app_name = "restaurant"

urlpatterns = [
    path("", views.home, name="home"),
    path("urun/<int:pk>/<slug:slug>/", views.product_detail, name="product_detail"),
]
