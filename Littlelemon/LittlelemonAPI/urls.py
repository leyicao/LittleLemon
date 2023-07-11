from django.urls import path, include
from . import views
# from rest_framework.authtoken.views import obtain_auth_token
# from rest_framework import routers

# router = routers.DefaultRouter()
# router.register('menu-items', views.MenuItemsView,  basename='menu-items')
# router.register('groups/manager/users', views.ManagerView,  basename='manager')
# router.register('groups/delivery-crew/users', views.DeliveryCrewView,  basename='delivery-crew')
# router.register('cart/menu-items', views.CartView,  basename='cart')

urlpatterns = [
    path('categories/', views.CategoriesView.as_view()),
    # path('api-token-auth/', obtain_auth_token),
    # path('', include(router.urls)),
    path('menu-items/', views.MenuItemsView.as_view()),
    path('menu-items/<int:pk>/', views.SingleMenuItemView.as_view()),
    path('cart/menu-items/', views.CartView.as_view()),
    path('orders/', views.OrderDetailView.as_view()),
    path('orders/<int:pk>/', views.SingleOrderDetailView.as_view()),
    path('groups/manager/users/', views.ManagerView.as_view({
        'get': 'list',
        'post': 'create',
        'delete': 'destroy'
    })),
    path('groups/delivery-crew/users/', views.DeliveryCrewView.as_view({
        'get': 'list',
        'post': 'create',
        'delete': 'destroy'
    })),
]