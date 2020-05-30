from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import logout, authenticate, login
from .forms import RegistrationForm, CouponForm, CheckoutForm, AddressForm, ShopkeeperContactForm, ItemForm
from .models import Address, Item, OrderItem, Coupon, Order, Payment, UserProfile, ShopkeeperContact
from django.views.generic import View, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.core.mail import send_mail
from shopingkart import settings
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.db.models import Q
import random
import string
import stripe
from django.views.generic.base import TemplateView

stripe.api_key = settings.STRIPE_SECRET_KEY


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


def Contact(request):
    if request.method == 'POST':
        form = ShopkeeperContactForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = ShopkeeperContactForm()
    return render(request, 'address.html', {'form': form})



@login_required()
def address(request):
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            return redirect('home')
    else:
        form = AddressForm()
    return render(request, 'address.html', {'form': form})


@login_required()
def AddProduct(request):
    if request.method == 'POST':
        form = ItemForm(request.POST)
        if form.is_valid():
            u = form.save(commit=False)
            u.user = request.user
            u.save()
            return redirect('home')
    else:
        form = ItemForm()
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


def is_valid_form(values):
    valid = True
    for field in values:
        if field == '':
            valid = False
    return valid


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
                default=True
            )
            if shipping_address_qs.exists():
                context.update(
                    {'default_shipping_address': shipping_address_qs[0]})
                print('***************************************address exists')
                return render(self.request, "payment.html", context)
                # return redirect('payment')
            # return render(self.request, "checkout.html", context)
            return redirect('address')
        except ObjectDoesNotExist:
            messages.info(self.request, "You do not have an active order")
            return redirect("checkout")

    # def post(self, *args, **kwargs):
    #     form = CheckoutForm(self.request.POST or None)
    #     try:
    #         order = Order.objects.get(user=self.request.user, ordered=False)
    #         if form.is_valid():
    #
    #             use_default_shipping = form.cleaned_data.get(
    #                 'use_default_shipping')
    #             if use_default_shipping:
    #                 print("Using the defualt shipping address")
    #                 address_qs = Address.objects.filter(
    #                     user=self.request.user,
    #                     address_type=address_type,
    #                     default=True
    #                 )
    #                 if address_qs.exists():
    #                     shipping_address = address_qs[0]
    #                     order.shipping_address = shipping_address
    #                     order.save()
    #                     return render(self.request, "payment.html", order)
    #                 else:
    #                     messages.info(
    #                         self.request, "No default shipping address available")
    #                     return redirect('checkout')
    #             else:
    #                 print("User is entering a new shipping address")
    #                 shipping_address1 = form.cleaned_data.get('shipping_address')
    #                 shipping_address2 = form.cleaned_data.get('shipping_address2')
    #                 shipping_country = form.cleaned_data.get('shipping_country')
    #                 shipping_zip = form.cleaned_data.get('shipping_zip')
    #                 phone = form.cleaned_data.get('phone')
    #                 address_type = form.cleaned_data.get('address_type')
    #
    #                 if is_valid_form([shipping_address1, shipping_address2, shipping_country, shipping_zip, phone, address_Type]):
    #                     shipping_address = Address(
    #                         user=self.request.user,
    #                         street_address=shipping_address1,
    #                         apartment_address=shipping_address2,
    #                         country=shipping_country,
    #                         zip=shipping_zip,
    #                         phone=phone,
    #                         address_type=address_type
    #                     )
    #                     shipping_address.save()
    #
    #                     order.shipping_address = shipping_address
    #                     order.save()
    #
    #                     set_default_shipping = form.cleaned_data.get(
    #                         'set_default_shipping')
    #                     if set_default_shipping:
    #                         shipping_address.default = True
    #                         shipping_address.save()
    #                         return render(self.request, "payment.html", order)
    #
    #                 else:
    #                     messages.info(
    #                         self.request, "Please fill in the required shipping address fields")
    #
    #                     return redirect('checkout')
    #     except ObjectDoesNotExist:
    #         messages.warning(self.request, "You do not have an active order")
    #         return redirect("order-summary")


class ItemSearch(ListView):
    model = Item
    template_name = 'home.html'

    def get_queryset(self, *args, **kwargs):
        val = self.request.GET.get("q")
        if val:
            object_list = Item.objects.filter(
                Q(title__icontains=val) |
                Q(category__icontains=val)|
                Q(description__icontains=val)|
                Q(slug__icontains=val)
                ).distinct()
        else:
            object_list  = Item.objects.none()
        return object_list



# def create_ref_code():
#     return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))


# class PaymentView(View):
#     def get(self, *args, **kwargs):
#         order = Order.objects.get(user=self.request.user, ordered=False)
#         if order.shipping_address:
#             context = {
#                 'order': order,
#                 'DISPLAY_COUPON_FORM': False
#             }
#             return render(self.request, "payment.html", context)
#             userprofile = self.request.user.userprofile
#             if userprofile.one_click_purchasing:
#                 # fetch the users card list
#                 cards = stripe.Customer.list_sources(
#                     userprofile.stripe_customer_id,
#                     limit=3,
#                     object='card'
#                 )
#                 card_list = cards['data']
#                 if len(card_list) > 0:
#                     # update the context with the default card
#                     context.update({
#                         'card': card_list[0]
#                     })
#             return render(self.request, "payment.html", context)
#         else:
#             messages.warning(
#                 self.request, "You have not added a shipping_address")
#             return redirect("checkout")
#
#     def post(self, *args, **kwargs):
#         order = Order.objects.get(user=self.request.user, ordered=False)
#
#         customer = stripe.Customer.create(
#             email=self.request.user.email,
#         )
#         customer.sources.create(source=self.request.POST['stripeToken'])
        # userprofile.stripe_customer_id = customer['id']
        # userprofile.one_click_purchasing = True
        # userprofile.save()

        # amount = int(order.get_total() * 100)


        # form = PaymentForm(self.request.POST)
        # userprofile = UserProfile.objects.get(user=self.request.user)
        # if form.is_valid():
        #     token = form.cleaned_data.get('stripeToken')
        #     save = form.cleaned_data.get('save')
        #     use_default = form.cleaned_data.get('use_default')
        #
        #     if save:
        #         if userprofile.stripe_customer_id != '' and userprofile.stripe_customer_id is not None:
        #             customer = stripe.Customer.retrieve(
        #                 userprofile.stripe_customer_id)
        #             customer.sources.create(source=token)
        #
        #         else:
        #             customer = stripe.Customer.create(
        #                 email=self.request.user.email,
        #             )
        #             customer.sources.create(source=token)
        #             userprofile.stripe_customer_id = customer['id']
        #             userprofile.one_click_purchasing = True
        #             userprofile.save()

            # amount = int(order.get_total() * 100)
        #
        # try:
        #
        #     if use_default or save:
        #         # charge the customer because we cannot charge the token more than once
        #         charge = stripe.Charge.create(
        #             amount=amount,
        #             currency="INR",
        #             # customer=userprofile.stripe_customer_id
        #         )
        #     else:
        #         # charge once off on the token
        #         charge = stripe.Charge.create(
        #             amount=amount,
        #             currency="INR",
        #             source=self.request.POST['stripeToken']
        #         )
        #
        #     # create the payment
        #     payment = Payment()
        #     payment.stripe_charge_id = charge['id']
        #     payment.user = self.request.user
        #     payment.amount = order.get_total()
        #     payment.save()
        #     print('******************************************************* payment save')
        #
        #     # assign the payment to the order
        #
        #     order_items = order.items.all()
        #     order_items.update(ordered=True)
        #     for item in order_items:
        #         item.save()
        #
        #     order.ordered = True
        #     order.payment = payment
        #     order.ref_code = create_ref_code()
        #     order.save()
        #
        #     messages.success(self.request, "Your order was successful!")
        #     return redirect("/")
        #
        # except stripe.error.CardError as e:
        #     body = e.json_body
        #     err = body.get('error', {})
        #     messages.warning(self.request, f"{err.get('message')}")
        #     return redirect("/")
        #
        # except stripe.error.RateLimitError as e:
        #     # Too many requests made to the API too quickly
        #     messages.warning(self.request, "Rate limit error")
        #     return redirect("/")
        #
        # except stripe.error.InvalidRequestError as e:
        #     # Invalid parameters were supplied to Stripe's API
        #     print(e)
        #     messages.warning(self.request, "Invalid parameters")
        #     return redirect("/")
        #
        # except stripe.error.AuthenticationError as e:
        #     # Authentication with Stripe's API failed
        #     # (maybe you changed API keys recently)
        #     messages.warning(self.request, "Not authenticated")
        #     return redirect("/")
        #
        # except stripe.error.APIConnectionError as e:
        #     # Network communication with Stripe failed
        #     messages.warning(self.request, "Network error")
        #     return redirect("/")
        #
        # except stripe.error.StripeError as e:
        #     # Display a very generic error to the user, and maybe send
        #     # yourself an email
        #     messages.warning(
        #         self.request, "Something went wrong. You were not charged. Please try again.")
        #     return redirect("/")
        #
        # except Exception as e:
        #     # send an email to ourselves
        #     messages.warning(
        #         self.request, "A serious error occurred. We have been notifed.")
        #     return redirect("/")
        #
        # messages.warning(self.request, "Invalid data received")
        # return redirect("payment")


class PaymentView(TemplateView):
    template_name = 'payment.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['key'] = "pk_test_7qyvzdWvNskoksO8u5u51qbn00C5mgJxcZ"
        return context

def charge(request): # new
    if request.method == 'POST':
        order = Order.objects.get(user=request.user, ordered=False)

        customer = stripe.Customer.create(
            email=request.user,
        )
        # customer.sources.create(source=request.POST['stripeToken'])
        charge = stripe.Charge.create(
            amount=int(order.get_total() * 100),
            currency='INR',
            description= order.items,
            source=request.POST['stripeToken']
        )

        payment = Payment()
        payment.stripe_charge_id = charge['id']
        payment.user = request.user
        payment.amount = order.get_total()
        payment.stripe_customer_id = customer['id']
        payment.save()

        order_items = order.items.all()
        order_items.update(ordered=True)
        for item in order_items:
            item.save()

        order.ordered = True
        order.payment = payment
        order.save()

        messages.success(request, "Your order was successful!")
        return render(request, 'home.html')
        # return redirect('/')