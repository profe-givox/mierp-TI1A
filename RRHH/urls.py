from django.urls import include, path
from .views import LoginAPIView


from . import views

urlpatterns = [
    path('horario/', views.horario, name='horario'),
     path('registro/', views.registro_entrada_salida, name='registro_entrada_salida'),
     path('login/', LoginAPIView.as_view(), name='login'),
     path('get_sucursales/', views.get_sucursales, name='sucursales'),
     path('get_empleados/', views.get_empleados, name="Empleados")
]