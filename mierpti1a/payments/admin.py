from django.contrib import admin
from .models import Pago, DetalleTarjeta, DetallePayPal, DetalleVale

# Definimos los inlines para los detalles de los pagos
class DetalleTarjetaInline(admin.StackedInline):
    model = DetalleTarjeta
    extra = 1  # Número de formularios adicionales que se muestran por defecto (puede ser 0 si no quieres mostrar de más)
    min_num = 0  # Número mínimo de formularios

class DetallePayPalInline(admin.StackedInline):
    model = DetallePayPal
    extra = 1

class DetalleValeInline(admin.StackedInline):
    model = DetalleVale
    extra = 1

# Configuración del ModelAdmin para Pago
@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ('cliente_id', 'tipo', 'monto', 'fecha_pago')
    list_filter = ('tipo',)

    # Agregamos los inlines a PagoAdmin
    inlines = [DetalleTarjetaInline, DetallePayPalInline, DetalleValeInline]

    # Mostramos u ocultamos inlines dependiendo del tipo de pago
    def get_inline_instances(self, request, obj=None):
        inlines = []
        if obj:
            if obj.tipo == 'Tarjeta':
                inlines.append(DetalleTarjetaInline(self.model, self.admin_site))
            elif obj.tipo == 'PayPal':
                inlines.append(DetallePayPalInline(self.model, self.admin_site))
            elif obj.tipo == 'Vale':
                inlines.append(DetalleValeInline(self.model, self.admin_site))
        return inlines
