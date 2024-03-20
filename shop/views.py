from typing import Any
from django.http import HttpRequest
from django.http.response import HttpResponse as HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import TemplateView, CreateView, FormView
from .models import *
from django.views import View
from .forms import *
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse_lazy
# Create your views here.
class HomeView(TemplateView):
    template_name = "home.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product_list = Product.objects.all().order_by("-id")
        context["product_list"] = product_list
        return context

    
class AllProductView(TemplateView):
    template_name = "all_product.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all()
        return context
    
    
class ProductDetailView(TemplateView):
    template_name = "product_detail.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        url_slug = self.kwargs["slug"]
        product = Product.objects.get(slug=url_slug)
        print(product)
        product.view_count += 1
        product.save()
        context["product"]=product
        return context
  
  
class AddToCartView(TemplateView):
    template_name = "add_to_cart.html"
    
    def get_context_data(self, **kwargs: Any):
        context = super().get_context_data(**kwargs)
        product_id = self.kwargs['pro_id']
        product_obj = Product.objects.get(id=product_id)
        cart_id = self.request.session.get('cart_id', None)
        
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
            this_product_in_cart = cart_obj.cartproduct_set.filter(product=product_obj) 
            print(this_product_in_cart)
            if this_product_in_cart.exists():
                cartproduct = this_product_in_cart.last()
                cartproduct.quantity += 1
                cartproduct.subtotal += product_obj.selling_price
                cartproduct.save()
                cart_obj.total += product_obj.selling_price
                cart_obj.save()
                print(cart_obj)
                print(product_obj)
            
            else:
                cartproduct = CartProduct.objects.create(
                    cart=cart_obj, product=product_obj, rate=product_obj.selling_price, quantity=1, subtotal=product_obj.selling_price)
                cart_obj.total += product_obj.selling_price
                cart_obj.save()               
            
        else:
            cart_obj = Cart.objects.create(total=0)
            self.request.session['cart_id'] = cart_obj.id
            cartproduct = CartProduct.objects.create(
                cart=cart_obj, product=product_obj, rate=product_obj.selling_price, quantity=1, subtotal=product_obj.selling_price)
            cart_obj.total += product_obj.selling_price
            cart_obj.save()

            
        
        return context
        

class MyCartView(TemplateView):
    template_name = "mycart.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_id = self.request.session.get("cart_id", None)
        if cart_id:
            cart = Cart.objects.get(id=cart_id)
        else:
            cart = None
        context['cart'] = cart
        return context
    
class ManageCartView(View):
    def get(self,request,*args,**kwargs):
        cp_id = self.kwargs["cp_id"]
        action = request.GET.get("action")
        cp_obj = CartProduct.objects.get(id=cp_id)
        cart_obj = cp_obj.cart
        if action=="inc":
            cp_obj.quantity +=1
            cp_obj.subtotal += cp_obj.rate
            cp_obj.save()
            cart_obj.total += cp_obj.rate
            cart_obj.save() 
        elif action=="dec":
            cp_obj.quantity -=1
            cp_obj.subtotal -= cp_obj.rate
            cp_obj.save()
            cart_obj.total -= cp_obj.rate
            cart_obj.save() 
            if cp_obj.quantity == 0:
                cp_obj.delete()
            
        elif action=="rem":
            cart_obj.total -= cp_obj.subtotal
            cart_obj.save()
            cp_obj.delete()
            
        else:
            pass
        return redirect("shop:my_cart")
    
    
   
class EmptyCartView(View):
    def get(self,request,*args,**kwargs):
        cart_id = request.session.get("cart_id", None)
        if cart_id:
            
            cart_obj = Cart.objects.get(id=cart_id)
            cart_obj.cartproduct_set.all().delete()
            cart_obj.total = 0
            cart_obj.save()
  
        return redirect("shop:my_cart")


class CheckoutView(CreateView):
    template_name = "checkout.html"
    form_class = CheckoutForm
    success_url = reverse_lazy("shop:home")
    
    def dispatch(self, request, *args, **kwargs) :
        
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs) :
        context = super().get_context_data(**kwargs)
        cart_id = self.request.session.get("cart_id", None)
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
        else:
            cart_obj = None
        context["cart"] = cart_obj
        return context
    
    def form_valid(self, form):
        cart_id = self.request.session.get("cart_id")
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
            form.instance.cart = cart_obj
            form.instance.subtotal = cart_obj.total
            form.instance.discount = 0
            form.instance.total = cart_obj.total
            form.instance.order_status = "Order Received"
            del self.request.session['cart_id']
        else:
            return redirect("shop:home")
        return super().form_valid(form)
    
    
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
        login(self.request,user)
        return super().form_valid(form)

        
        
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
        print(usr.customer)
        if usr is not None and usr.customer:
            login(self.request, usr)
        else:
            return render(self.request, "customer_login.html", {"form":self.form_class}, {"error":"Invalid credential"})
            
        
        return super().form_valid(form)
    

       
class AboutView(TemplateView):
    template_name = "about.html"
