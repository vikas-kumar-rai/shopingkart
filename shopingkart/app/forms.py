from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomerRegistration, Address, Item
from django.contrib.auth import get_user_model
# from django_countries.fields import CountryField
# from django_countries.widgets import CountrySelectWidget



# User = get_user_model

class RegistrationForm(UserCreationForm):
    class Meta:
        model = CustomerRegistration
        fields = ('full_name', 'email', )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        qs = get_user_model().objects.filter(email=email)
        if qs.exists():
            raise forms.ValidationError("email is taken")
        return email



class ShopkeeperRegForm(UserCreationForm):
    class Meta:
        model = CustomerRegistration
        fields = ('full_name', 'email', )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        qs = get_user_model().objects.filter(email=email)
        if qs.exists():
            raise forms.ValidationError("email is taken")
        return email

    def save(self):
        get_user_model().is_shopkeeper = True
        user = super(ShopkeeperRegForm, self).save()

        return user


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        # fields = '__all__'
        fields = ['street_address', 'apartment_address', 'country', 'zip', 'address_type', 'phone', ]

        def form_valid(self, form):
            address = form.save(commit=False)
            address.user = CustomerRegistration.objects.get(customer_id=self.kwargs['customer_id'])
            address.save()

class CouponForm(forms.Form):
    code = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Promo code',
        'aria-label': 'Recipient\'s username',
        'aria-describedby': 'basic-addon2'
    }))

