from django import forms
from .models import Ticket

class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['title', 'description', 'status']  # Campos que aparecerán en el formulario

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Aplicar clases de Bootstrap a todos los campos
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})
        
        # Limitar las opciones del campo "status"
        self.fields['status'].choices = [
            ('open', 'Abierto'),
            ('resolved', 'Resuelto'),
        ]