from django.urls import path
from . import views 

urlpatterns = [
    path('',views.index),
    path('pagos/',views.pagos),
    path('cuentas/',views.cuentas),
    path('informes/',views.informes),
    path('disputas/',views.disputas),
]