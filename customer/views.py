from typing import Any
from django.http import HttpRequest
from django.http.response import HttpResponse as HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import TemplateView, CreateView, FormView, DetailView, ListView
from shop.models import *
from django.views import View
from shop.forms import *
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse_lazy
from shop.views import ShopMixin
# Create your views here.

# Create your views here.
class CustomerRegistrationView(CreateView):
    template_name = "customer_registration.html"
    form_class = CustomerRegistrationForm
    success_url = reverse_lazy("shop:home")

    def form_valid(self, form):
       
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")
        email = form.cleaned_data.get("email")
        user = User.objects.create_user(username, password, email)
        form.instance.user = user
        print(form.cleaned_data)
        login(self.request,user)
        return super().form_valid(form)
    
    def get_success_url(self):
        if 'next' in self.request.GET:
            next_url = self.request.GET.get("next")
            return next_url
        else:
            return self.success_url

        
        
class CustomerLogoutView(View):
    def get(self, request):
        logout(request)
        return redirect("shop:customer_login")
    

class CustomerLoginView(FormView):
    template_name = "customer_login.html"
    form_class = CustomerLoginForm
    success_url = reverse_lazy("shop:home")
    def form_valid(self, form):
        uname = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")
        usr = authenticate(username = uname, password = password)
        print(usr)
        
        if usr is not None and Customer.objects.filter(user=usr).exists():
            login(self.request, usr)
        else:
            return render(self.request, "customer_login.html", {"form": self.form_class, "error": "Invalid credential"})

        return super().form_valid(form)
    
    def get_success_url(self):
        if 'next' in self.request.GET:
            print(self.request.GET)
            next_url = self.request.GET.get("next")
            return next_url
        else:
            return self.success_url
            

   
class CustomerProfileView(ShopMixin,TemplateView):
    template_name = "customer_profile.html"
    
    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if request.user.is_authenticated and Customer.objects.filter(user=user).exists():
            print("llog")
        else:
            return redirect("/customer-login/?next=/customer-profile/")
        print(user)
        return super().dispatch(request, *args, **kwargs)
        
    def get_context_data(self, **kwargs: Any) :
        context = super().get_context_data(**kwargs)
        customer = self.request.user.customer
        context['customer'] = customer
        context['orders'] = Order.objects.filter(cart__customer=customer).order_by("-id")
        return context
    
    
class OrderDetailsView(DetailView):
    template_name = "orderdetails.html"
    model = Order
    context_object_name = "ord_obj"

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if request.user.is_authenticated and Customer.objects.filter(user=user).exists():
            order_id = self.kwargs["pk"]
            order = Order.objects.get(id=order_id)
            if request.user.customer != order.cart.customer:
                return redirect("shop:customer_profile")
        else:
            return redirect("/customer-login/?next=/customer-profile/")
        print(user)
        return super().dispatch(request, *args, **kwargs)
    
   