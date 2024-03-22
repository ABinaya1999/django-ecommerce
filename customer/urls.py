from django.urls import path
from .views import *
app_name = 'customer'
urlpatterns = [
    path('customer-registration/', CustomerRegistrationView.as_view(), name="customer_registration"),
    path('customer-logout/', CustomerLogoutView.as_view(), name="customer_logout"),
    path('customer-login/', CustomerLoginView.as_view(), name="customer_login"),
    
    path('customer-profile/',CustomerProfileView.as_view(), name="customer_profile"),
    path('customer-profile/order-<int:pk>',OrderDetailsView.as_view(), name="order_details"),
]