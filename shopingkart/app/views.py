from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import logout, authenticate, login
from .forms import RegistrationForm, ShopkeeperRegForm, AddressForm, CouponForm
from .models import Address, Item, OrderItem, Coupon, Order
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


class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order
            }
            return render(self.request, 'order_summary.html', context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("/")



@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "This item quantity was updated.")
            return redirect("order-summary")
        else:
            order.items.add(order_item)
            messages.info(request, "This item was added to your cart.")
            return redirect("order-summary")
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, "This item was added to your cart.")
        return redirect("order-summary")


@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            order.items.remove(order_item)
            order_item.delete()
            messages.info(request, "This item was removed from your cart.")
            return redirect("order-summary")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("product", slug=slug)
    else:
        messages.info(request, "You do not have an active order")
        return redirect("product", slug=slug)


@login_required
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
            messages.info(request, "This item quantity was updated.")
            return redirect("order-summary")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("product", slug=slug)
    else:
        messages.info(request, "You do not have an active order")
        return redirect("product", slug=slug)


def get_coupon(request, code):
    try:
        coupon = Coupon.objects.get(code=code)
        return coupon
    except ObjectDoesNotExist:
        messages.info(request, "This coupon does not exist")
        return redirect("checkout")


class AddCouponView(View):
    def post(self, *args, **kwargs):
        form = CouponForm(self.request.POST or None)
        if form.is_valid():
            try:
                code = form.cleaned_data.get('code')
                order = Order.objects.get(
                    user=self.request.user, ordered=False)
                order.coupon = get_coupon(self.request, code)
                order.save()
                messages.success(self.request, "Successfully added coupon")
                return redirect("checkout")
            except ObjectDoesNotExist:
                messages.info(self.request, "You do not have an active order")
                return redirect("checkout")
