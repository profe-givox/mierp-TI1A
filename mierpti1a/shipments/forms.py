from django import forms
from .models import Order, Address

class OrderForm(forms.ModelForm):
    address = forms.ModelChoiceField(queryset=Address.objects.none(), required=True)

    class Meta:
        model = Order
        fields = ['product', 'quantity', 'status', 'address']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['address'].queryset = Address.objects.filter(user=user)


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['street', 'city', 'state', 'postal_code', 'latitude', 'longitude']