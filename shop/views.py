from typing import Any
from django.http import HttpRequest, JsonResponse
from django.http.response import HttpResponse as HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import TemplateView, CreateView, FormView, DetailView, ListView
from .models import *
from django.db.models import Q
from django.views import View
from .forms import *
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse_lazy, reverse
from django.core.paginator import Paginator
from django.contrib import messages
import requests
# Create your views here.

class ShopMixin(object):
    def dispatch(self,request, *args, **kwargs):
        cart_id = request.session.get("cart_id")
        if cart_id:
            cart_obj = Cart.objects.get(id = cart_id)
            if request.user.is_authenticated and request.user.customer:
                cart_obj.customer = request.user.customer
                cart_obj.save()
        
        return super().dispatch(request, *args, **kwargs)
    
    
    
class HomeView(ShopMixin,TemplateView):
    template_name = "home.html"
    
    def get_context_data(self, **kwargs):   
        context = super().get_context_data(**kwargs)
        product_list = Product.objects.all().order_by("-id")
        paginator = Paginator(product_list, 3)
        page_number = self.request.GET.get("page")
        product_list = paginator.get_page(page_number)
        context["product_list"] = product_list
        return context

    
class AllProductView(ShopMixin,TemplateView):
    template_name = "all_product.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_list = Category.objects.all()
        paginator = Paginator(category_list, 1)
        page_number = self.request.GET.get("page")
        category_list = paginator.get_page(page_number)
        context["category_list"] = category_list
        return context
    
    
class ProductDetailView(ShopMixin,TemplateView):
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
  
  
class AddToCartView(ShopMixin,TemplateView):
    
    def get(self,request,*args, **kwargs):
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

            
        messages.success(self.request, 'Product added to the cart!')
        
        if request.META.get('HTTP_REFERER') and '/all-product/' in request.META.get('HTTP_REFERER'):
        
            return redirect(request.META.get('HTTP_REFERER'))
        
        elif request.META.get('HTTP_REFERER') and '/product/' in request.META.get('HTTP_REFERER'):
     
            print(request.META.get('HTTP_REFERER'))
            return redirect(request.META.get('HTTP_REFERER'))
        
        else:

            return redirect("shop:home")
        

class MyCartView(ShopMixin,TemplateView):
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
    
class ManageCartView(ShopMixin,View):
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
    
    
   
class EmptyCartView(ShopMixin,View):
    def get(self,request,*args,**kwargs):
        cart_id = request.session.get("cart_id", None)
        if cart_id:
            
            cart_obj = Cart.objects.get(id=cart_id)
            cart_obj.cartproduct_set.all().delete()
            cart_obj.total = 0
            cart_obj.save()
  
        return redirect("shop:my_cart")


class CheckoutView(ShopMixin,CreateView):
    template_name = "checkout.html"
    form_class = CheckoutForm
    success_url = reverse_lazy("shop:home")
    
    def dispatch(self, request, *args, **kwargs) :
        user = request.user
        if request.user.is_authenticated and request.user.customer:
            print("llog")
        else:
            return redirect("/customer/customer-login/?next=/checkout/")
        print(user)
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
            method = form.cleaned_data.get("payment_method")
            order = form.save()
            print(order)
            del self.request.session['cart_id']
            if method == "Esewa":
                return redirect(reverse("shop:esewa_request") + "?o_id=" + str(order.id))
            
            
        else:
            return redirect("shop:home")
        return super().form_valid(form)
    
    
class SearchView(TemplateView):
    template_name = "search.html" 
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        kw = self.request.GET.get("keyword")
        product = Product.objects.filter(Q(title__icontains=kw) | Q(description__icontains=kw))
        print(product)
        context["product"]=product
        
        return context


class EsewaRequestView(View):
    
    def get(self, request, *args, **kwargs):
        order_id = request.GET.get("o_id")
        order = Order.objects.get(id= order_id)
        context = {"order": order}
        return render(request, "esewa_request.html", context)
    

class EsewaVerifyView(View):
    
    def get(self, request, *args, **kwargs):
        import xml.etree.ElementTree as ET
        oid = request.GET.get("oid")
        amt = request.GET.get("amt")
        refId = request.GET.get("refId")
        url = "https://uat.esewa.com.np/epay/transrec"
        d = {
            'amt': amt,
            'scd': 'epay_payment',
            'rid': refId,
            'pid': oid,
        }
        resp = requests.post(url, d)
        root = ET.fromstring(resp.content)
        status = root[0].text.strip()
        o_id = oid.split("_")[1]
        order_obj = Order.objects.get(id=int(o_id))
        if status == "Success":
            order_obj.payment_method = True
            order_obj.save()
            return redirect("/")
        else:
            
            return redirect("/esewa-request/" + "?o_id" + o_id)
        
        return redirect("/")
    
    
    
    
class AboutView(ShopMixin,TemplateView):
    template_name = "about.html"
    




