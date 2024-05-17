from django import forms


class CheckoutForm(forms.Form):
    shipping_address = forms.CharField(
        max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}))
    city = forms.CharField(max_length=100, widget=forms.TextInput(
        attrs={'class': 'form-control'}))
    postal_code = forms.CharField(
        max_length=20, widget=forms.TextInput(attrs={'class': 'form-control'}))
