from django.urls import path
from .views import *
app_name = 'shop'
urlpatterns = [
    path('', HomeView.as_view(), name="home"),
    path('all-product/', AllProductView.as_view(), name="all_product"),
    path('about/', AboutView.as_view(), name="about"),
    path('product/<slug:slug>/', ProductDetailView.as_view(), name="product_detail"),
    
    path('add-to-cart-<int:pro_id>', AddToCartView.as_view(), name="add_to_cart"),
    path('mycart/', MyCartView.as_view(), name="my_cart"),
    path('manage-cart/<int:cp_id>', ManageCartView.as_view(), name="manage_cart"),
    path('empty-cart/', EmptyCartView.as_view(), name="empty_cart"),
     
    path('checkout/', CheckoutView.as_view(), name="checkout"),
    
    ###customer####
    path('customer-registration/', CustomerRegistrationView.as_view(), name="customer_registration"),
    path('customer-logout/', CustomerLogoutView.as_view(), name="customer_logout"),
    path('customer-login/', CustomerLoginView.as_view(), name="customer_login"),
    
    path('customer-profile/',CustomerProfileView.as_view(), name="customer_profile"),
    path('customer-profile/order-<int:pk>',OrderDetailsView.as_view(), name="order_details"),
    
    ######admin####
    path('admin-home/', AdminHomeView.as_view(), name="admin_home"),
    path('admin-login/', AdminLoginView.as_view(), name="admin_login"),
    path('admin-order/<int:pk>/', AdminOrderDetailView.as_view(), name="admin_order_detail"),
    
    path('admin-all-orders/', AdminOrderListView.as_view(), name="admin_order_list"),
    path('admin-order-<int:pk>-change', AdminOrderStatusChangeView.as_view(), name="admin_order_status_change"),
    
]
