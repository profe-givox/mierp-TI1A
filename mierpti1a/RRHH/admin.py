from django.contrib import admin
from django import forms
from RRHH.models import Departamento, Empleado, Puesto, Sucursal

admin.site.register(Sucursal)
admin.site.register(Departamento)
admin.site.register(Puesto)
admin.site.register(Empleado)



