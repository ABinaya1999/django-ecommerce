from django.urls import path
from .views import *
app_name = 'owner'
urlpatterns = [
    path('admin-home/', AdminHomeView.as_view(), name="admin_home"),
    path('admin-login/', AdminLoginView.as_view(), name="admin_login"),
    path('admin-order/<int:pk>/', AdminOrderDetailView.as_view(), name="admin_order_detail"),
    
    path('admin-all-orders/', AdminOrderListView.as_view(), name="admin_order_list"),
    path('admin-order-<int:pk>-change', AdminOrderStatusChangeView.as_view(), name="admin_order_status_change"),
    
]