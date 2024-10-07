from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("punto_de_venta/", include("punto_de_venta.urls")),
    path("admin/", admin.site.urls),
]