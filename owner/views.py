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

class AdminLoginView(FormView):
    template_name = "adminpages/admin_login.html"
    form_class = AdminLoginForm
    success_url = reverse_lazy("owner:admin_home")
    
    def form_valid(self,form):
        uname = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")
        usr = authenticate(username = uname, password = password)
        print(usr)
        
        if usr is not None and Admin.objects.filter(user=usr).exists():
            login(self.request, usr)
        else:
            return render(self.request, self.template_name, {"form": self.form_class, "error": "Invalid credential"})

        return super().form_valid(form)
        
class AdminRequiredMixin(object):
    def dispatch(self, request, *args, **kwargs) :
        user = request.user
        if request.user.is_authenticated and Admin.objects.filter(user=user).exists():
            print("llog")
        else:
            return redirect("owner/admin-login/")
        print(user)
        return super().dispatch(request, *args, **kwargs)
   
class AdminHomeView(AdminRequiredMixin,TemplateView):
    template_name = "adminpages/admin_home.html"
    
    def get_context_data(self, **kwargs):
        context =super().get_context_data(**kwargs)
        context["pending_orders"] = Order.objects.filter(order_status="Order Received").order_by("-id")
        return context
    
class AdminOrderDetailView(AdminRequiredMixin,DetailView):
    template_name = "adminpages/admin_orderdetail.html"
    model = Order
    context_object_name = "ord_obj"
    
    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        context["allstatus"] = ORDER_STATUS
        return context
    
class AdminOrderListView(AdminRequiredMixin, ListView):
    template_name = "adminpages/admin_orderlist.html"
    queryset = Order.objects.all().order_by("-id")
    context_object_name = "ord_obj"
    
    
class AdminOrderStatusChangeView(AdminRequiredMixin, View):
    def post(self,request, *args, **kwargs):
        order_id = self.kwargs["pk"]
        order_obj = Order.objects.get(id=order_id)
        new_status = request.POST.get("status")
        order_obj.order_status = new_status
        order_obj.save()
        
        return redirect(reverse_lazy("owner:admin_order_detail", 
                         kwargs={"pk": self.kwargs["pk"]}))