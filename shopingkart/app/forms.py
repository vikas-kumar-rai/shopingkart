from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomerRegistration


class RegistrationForm(UserCreationForm):
    class Meta:
        model = CustomerRegistration
        fields = ('full_name', 'email', )