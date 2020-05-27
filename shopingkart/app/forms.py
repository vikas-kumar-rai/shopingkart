from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomerRegistration, Address, Item
from django.contrib.auth import get_user_model
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget



# User = get_user_model
ADDRESS_CHOICES = (
    ('H', 'Home'),
    ('O', 'Office'),
)

PAYMENT_CHOICES = (
    ('D', 'Debit Card'),
    ('P', 'Paytm')
)


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

#
# class AddressForm(forms.ModelForm):
#     class Meta:
#         model = Address
#         # fields = '__all__'
#         fields = ['street_address', 'apartment_address', 'country', 'zip', 'address_type', 'phone', ]
#
#         def form_valid(self, form):
#             address = form.save(commit=False)
#             address.user = CustomerRegistration.objects.get(customer_id=self.kwargs['customer_id'])
#             address.save()

class CouponForm(forms.Form):
    code = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Promo code',
        'aria-label': 'Recipient\'s username',
        'aria-describedby': 'basic-addon2'
    }))


class CheckoutForm(forms.Form):
    shipping_address = forms.CharField(required=True)
    shipping_address2 = forms.CharField(required=False)
    shipping_country = CountryField(blank_label='(select country)').formfield(
        required=True,
        widget=CountrySelectWidget(attrs={
            'class': 'custom-select d-block w-100',
        }))
    shipping_zip = forms.CharField(required=True)
    phone = forms.IntegerField(required=True)

    address_type = forms.ChoiceField(
        widget=forms.RadioSelect, choices=ADDRESS_CHOICES)

    # billing_address = forms.CharField(required=False)
    # billing_address2 = forms.CharField(required=False)
    # billing_country = CountryField(blank_label='(select country)').formfield(
    #     required=False,
    #     widget=CountrySelectWidget(attrs={
    #         'class': 'custom-select d-block w-100',
    #     }))
    # billing_zip = forms.CharField(required=False)
    #
    # same_billing_address = forms.BooleanField(required=False)
    # set_default_shipping = forms.BooleanField(required=False)
    use_default_shipping = forms.BooleanField(required=False)
    # set_default_billing = forms.BooleanField(required=False)
    # use_default_billing = forms.BooleanField(required=False)

    payment_option = forms.ChoiceField(
        widget=forms.RadioSelect, choices=PAYMENT_CHOICES)


