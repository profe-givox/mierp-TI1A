from django import forms
from .models import Ticket, Empleado

class TicketUpdateForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['status', 'assigned_to']

        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
        }

        labels = {
            'status': 'Estado',
            'assigned_to': 'Usuario del Soporte',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['assigned_to'].queryset = Empleado.objects.all()  # Lista de empleados
