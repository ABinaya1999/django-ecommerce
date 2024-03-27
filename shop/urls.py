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
    path('search/', SearchView.as_view(), name="search" ),
    
    path('esewa-request/', EsewaRequestView.as_view(), name="esewa_request"),
    path('esewa-verify/', EsewaVerifyView.as_view(), name="esewa_verify"),
    # path('search/', SearchView.as_view(), name="search" ),
    
    
    
    
]
