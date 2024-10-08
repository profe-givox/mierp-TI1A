from django.contrib import admin
from .models import Cliente, Pago, Efectivo, Tarjeta, Vale, FacturaPorCobrar, GestionDisputaDePagos

# Register your models here.
admin.site.register(Cliente)
admin.site.register(Pago)
admin.site.register(Efectivo)
admin.site.register(Tarjeta)
admin.site.register(Vale)
admin.site.register(FacturaPorCobrar)
admin.site.register(GestionDisputaDePagos)