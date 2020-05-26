from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import logout, authenticate, login
from .forms import RegistrationForm, ShopkeeperRegForm, AddressForm
from .models import Address, Item
from django.views.generic import View, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.core.mail import send_mail
from shopingkart import settings
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.contrib.auth.decorators import login_required


import random
import string
import stripe
# stripe.api_key = settings.STRIPE_SECRET_KEY


class Home(ListView):
    model = Item
    template_name = 'home.html'


def loginUser(request):
    if request.method=="POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        print(user)
        if user is not None:
            login(request, user)
            return redirect("/")

        else:
            return render(request, 'login.html')

    return render(request, 'login.html')


def logoutUser(request):
    logout(request)
    return redirect("/login")


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get("email")
            form.save()
            subject = 'registration'
            msg = "successfully register"
            print("njsnjn", email)
            to = email
            res = send_mail(subject, msg, settings.EMAIL_HOST_USER, [to])
            if (res == 1):
                msg = "Mail sent"
                print("mail sent")
            else:
                msg = "Mail could not send"

            return redirect('login')
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})



def shopkeeper_reg(request):
    if request.method == 'POST':
        form = ShopkeeperRegForm(request.POST)
        if form.is_valid():
            request.user.is_shopkeeper = True
            email = form.cleaned_data.get("email")
            form.save()
            subject = 'registration'
            msg = "successfully register"
            print("njsnjn", email)
            to = email
            res = send_mail(subject, msg, settings.EMAIL_HOST_USER, [to])
            if (res == 1):
                msg = "Mail sent"
                print("mail sent")
            else:
                msg = "Mail could not send"

            return redirect('login')
    else:
        form = ShopkeeperRegForm()
    return render(request, 'register.html', {'form': form})
#
# class AddressView(view):
#     form = AddressForm()
#
#     def get(self, request, id, *args, **kwargs):
#         address = Address.objects.filter(user=id)
#         context = {
#             'obj': address,
#             'form': self.form
#         }
#         return render(request, 'index.html', context)
#
#     def post(self, request, *args, **kwargs):
#         if form.is_valid():
#             form.save()
#             return redirect('home')
#         return redirect("address.html")

@login_required()
def address(request):
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            # print('form ins goning to save ***********************', form)
            form.save()
            return redirect('home')
    else:
        form = AddressForm()
    return render(request, 'address.html', {'form': form})


class ItemDetailView(DetailView):
    model = Item
    template_name = "product.html"