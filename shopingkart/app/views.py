from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import logout, authenticate, login
from .forms import RegistrationForm, ShopkeeperRegForm, CouponForm, CheckoutForm
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
        if form.is_valid([shipping_address, shipping_address2, shipping_country, shipping_zip, phone, address_type]):
            shipping_address = Address(
                user=self.request.user,
                street_address=shipping_address,
                apartment_address=shipping_address2,
                country=shipping_country,
                zip=shipping_zip,
                phone=phone,
                address_type=address_type
            )
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


class CheckoutView(View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            form = CheckoutForm()
            context = {
                'form': form,
                'couponform': CouponForm(),
                'order': order,
                'DISPLAY_COUPON_FORM': True
            }

            shipping_address_qs = Address.objects.filter(
                user=self.request.user,
                address_type='S',
                default=True
            )
            if shipping_address_qs.exists():
                context.update(
                    {'default_shipping_address': shipping_address_qs[0]})

            # billing_address_qs = Address.objects.filter(
            #     user=self.request.user,
            #     address_type='B',
            #     default=True
            # )
            # if billing_address_qs.exists():
            #     context.update(
            #         {'default_billing_address': billing_address_qs[0]})

            return render(self.request, "checkout.html", context)
        except ObjectDoesNotExist:
            messages.info(self.request, "You do not have an active order")
            return redirect("checkout")

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():

                use_default_shipping = form.cleaned_data.get(
                    'use_default_shipping')
                if use_default_shipping:
                    print("Using the defualt shipping address")
                    address_qs = Address.objects.filter(
                        user=self.request.user,
                        address_type=address_type,
                        default=True
                    )
                    if address_qs.exists():
                        shipping_address = address_qs[0]
                        order.shipping_address = shipping_address
                        order.save()
                    else:
                        messages.info(
                            self.request, "No default shipping address available")
                        return redirect('checkout')
                else:
                    print("User is entering a new shipping address")
                    shipping_address1 = form.cleaned_data.get(
                        'shipping_address')
                    shipping_address2 = form.cleaned_data.get(
                        'shipping_address2')
                    shipping_country = form.cleaned_data.get(
                        'shipping_country')
                    shipping_zip = form.cleaned_data.get('shipping_zip')

                    if is_valid_form([shipping_address, shipping_address2, shipping_country, shipping_zip, phone, address_type]):
                        shipping_address = Address(
                            user=self.request.user,
                            street_address=shipping_address,
                            apartment_address=shipping_address2,
                            country=shipping_country,
                            zip=shipping_zip,
                            phone=phone,
                            address_type=address_type
                        )
                        shipping_address.save()

                        order.shipping_address = shipping_address
                        order.save()

                        set_default_shipping = form.cleaned_data.get(
                            'set_default_shipping')
                        if set_default_shipping:
                            shipping_address.default = True
                            shipping_address.save()

                    else:
                        messages.info(
                            self.request, "Please fill in the required shipping address fields")
                #
                # use_default_billing = form.cleaned_data.get(
                #     'use_default_billing')
                # same_billing_address = form.cleaned_data.get(
                #     'same_billing_address')
                #
                # if same_billing_address:
                #     billing_address = shipping_address
                #     billing_address.pk = None
                #     billing_address.save()
                #     billing_address.address_type = 'B'
                #     billing_address.save()
                #     order.billing_address = billing_address
                #     order.save()
                #
                # elif use_default_billing:
                #     print("Using the defualt billing address")
                #     address_qs = Address.objects.filter(
                #         user=self.request.user,
                #         address_type='B',
                #         default=True
                #     )
                #     if address_qs.exists():
                #         billing_address = address_qs[0]
                #         order.billing_address = billing_address
                #         order.save()
                #     else:
                #         messages.info(
                #             self.request, "No default billing address available")
                #         return redirect('checkout')
                # else:
                #     print("User is entering a new billing address")
                #     billing_address1 = form.cleaned_data.get(
                #         'billing_address')
                #     billing_address2 = form.cleaned_data.get(
                #         'billing_address2')
                #     billing_country = form.cleaned_data.get(
                #         'billing_country')
                #     billing_zip = form.cleaned_data.get('billing_zip')
                #
                #     if is_valid_form([billing_address1, billing_country, billing_zip]):
                #         billing_address = Address(
                #             user=self.request.user,
                #             street_address=billing_address1,
                #             apartment_address=billing_address2,
                #             country=billing_country,
                #             zip=billing_zip,
                #             address_type='B'
                #         )
                #         billing_address.save()
                #
                #         order.billing_address = billing_address
                #         order.save()
                #
                #         set_default_billing = form.cleaned_data.get(
                #             'set_default_billing')
                #         if set_default_billing:
                #             billing_address.default = True
                #             billing_address.save()
                #
                #     else:
                #         messages.info(
                #             self.request, "Please fill in the required billing address fields")

                payment_option = form.cleaned_data.get('payment_option')

                if payment_option == 'D':
                    return redirect('payment', payment_option='stripe')
                elif payment_option == 'P':
                    return redirect('payment', payment_option='paypal')
                else:
                    messages.warning(
                        self.request, "Invalid payment option selected")
                    return redirect('checkout')
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("order-summary")
