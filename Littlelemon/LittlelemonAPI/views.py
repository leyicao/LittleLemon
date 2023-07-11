from django.shortcuts import get_object_or_404
from .models import MenuItem, Category, Cart, Order, OrderItem
from rest_framework import generics, status, viewsets, mixins
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .serializers import MenuItemSerializer, CategorySerializer, UserSerializer, CartSerializer, OrderSerializer
from django.contrib.auth.models import User, Group
from decimal import *

# Create your views here.
class CategoriesView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        permission_classes = []
        if self.request.method != 'GET':
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

class MenuItemsView(generics.ListCreateAPIView): # viewsets.ModelViewSet
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    ordering_fields = ['price', 'inventory']
    search_fields = ['category__title']

    def get_permissions(self):
        permission_classes = []
        if self.request.method != 'GET':
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    # def update(self, request, *args, **kwargs):
    #     kwargs['partial'] = True
    #     return super().update(request, *args, **kwargs)

class SingleMenuItemView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

    def get_permissions(self):
        permission_classes = []
        if self.request.method != 'GET':
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

class ManagerView(viewsets.ViewSet):
    # mixins.ListModelMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet
    # queryset = User.objects.filter(groups=1)
    # serializer_class = UserSerializer
    # permission_classes = [IsAdminUser]
    permission_classes = [IsAdminUser]
    
    def list(self, request):
        users = User.objects.all().filter(groups__name='Manager')
        items = UserSerializer(users, many=True)
        return Response(items.data)
    
    def create(self, request):
        user = get_object_or_404(User, username=request.data['username'])
        managers = Group.objects.get(name='Manager')
        managers.user_set.add(user)
        return Response({'message': 'user added to the manager group'}, status.HTTP_201_CREATED)
    
    def destory(self, request):
        user = get_object_or_404(User, username=request.data['username'])
        managers = Group.objects.get(name='Manager')
        managers.user_set.remove(user)
        return Response({'message': 'user removed from the manager group'}, status.HTTP_200_OK)

class DeliveryCrewView(viewsets.ViewSet):
    # mixins.ListModelMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet
    # queryset = User.objects.filter(groups=2)
    # serializer_class = UserSerializer
    # permission_classes = [IsAdminUser]
    permission_classes = [IsAuthenticated]

    def list(self, request):
        users = User.objects.all().filter(groups__name='Delivery crew')
        items = UserSerializer(users, many=True)
        return Response(items.data)
    
    def create(self, request):
        if not self.request.user.is_superuser:
            if not self.request.user.groups.filter(name='Manager').exists():
                return Response({'message': 'forbidden'}, status.HTTP_403_FORBIDDEN)
        
        user = get_object_or_404(User, username=request.data['username'])
        dc = Group.objects.get(name='Delivery crew')
        dc.user_set.add(user)
        return Response({'message': 'user added to the delivery crew group'}, status.HTTP_200_OK)
    
    def destroy(self, request):
        if not self.request.user.is_superuser:
            if not self.request.user.groups.filter(name='Manager').exists():
                return Response({'message': 'forbidden'}, status.HTTP_403_FORBIDDEN)
        
        user = get_object_or_404(User, username=request.data['username'])
        dc = Group.objects.get(name='Delivery crew')
        dc.user_set.remove(user)
        return Response({'message': 'user removed from the delivery crew group'}, status.HTTP_200_OK)
    
class CartView(generics.ListCreateAPIView): # viewsets.ModelViewSet
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    # def list(self, request):
    #     user = request.user
    #     serializer = self.get_serializer(self.queryset.filter(user=user), many=True)
    #     return self.get_paginated_response(self.paginate_queryset(serializer.data))
    
    # def perform_create(self, serializer):
    #     user = self.request.user
    #     menuitem_id = self.request.data.get('menuitem')
    #     quantity = int(self.request.data.get('quantity'))
    #     menuitem = MenuItemSerializer(MenuItem.objects.get(pk=menuitem_id))
    #     unit_price = Decimal(menuitem.data.get('price'))
    #     price = unit_price * quantity
    #     serializer.save(user=user, price=price)
    #     return Response(serializer.data, status.HTTP_201_CREATED)

    # def delete(self, request, *args, **kwargs):
    #     user = request.user
    #     queryset = self.queryset.filter(user=user)
    #     queryset.delete()
    #     return Response(status=status.HTTP_204_NO_CONTENT)
    def get_queryset(self):
        return Cart.objects.all().filter(user=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        Cart.objects.all().filter(user=self.request.user).delete()
        return Response('ok')

class OrderDetailView(generics.ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    
    # managers = User.objects.filter(groups__name='Manager')
    # delivery_crew = User.objects.filter(groups__name='Delivery crew')

    def get_queryset(self):
        # user = self.request.user
        # if user in self.managers:
        #     return self.queryset
        # elif user in self.delivery_crew:
        #     return self.queryset.filter(delivery_crew=user)
        # else:
        #     return self.queryset.filter(user=user)
        if self.request.user.is_superuser:
            return Order.objects.all()
        elif self.request.user.groups.count() == 0: # normal customer - no groups
            return Order.objects.all().filter(user=self.request.user)
        elif self.request.user.groups.filter(name='Deliver crew').exists():
            return Order.objects.all().filter(delivery_crew=self.request.user)
        else:
            return Order.objects.all()
    
    # def perform_create(self, serializer):
    #     user = self.request.user
    #     cart_items = Cart.objects.filter(user=user)
    #     total = self.calculate_total(cart_items)
    #     order = serializer.save(user=user, total=total)
    #     for cart_item in cart_items:
    #         OrderItem.objects.create(order=order,menuitem=cart_item.menuitem, unit_price=cart_item.unit_price,
    #                                  quantity=cart_item.quantity, price=cart_item.price)
    #         cart_item.delete()
    #     return Response(serializer.data, status=status.HTTP_201_CREATED)

    # def calculate_total(self, cart_items):
    #     total = Decimal(0)
    #     for item in cart_items:
    #         total += item.price
    #     return total

    def create(self, request, *args, **kwargs):
        menuitem_count = Cart.objects.all().filter(user=self.request.user).count()
        if menuitem_count == 0:
            return Response({"message": "no item in cart"})
        
        data = request.data.copy()
        total = self.get_total_price(self.request.user)
        data['total'] = total
        data['user'] = self.request.user.id
        order_serializer = OrderSerializer(data=data)
        if (order_serializer.is_valid()):
            order = order_serializer.save()

            items = Cart.objects.all().filter(user=self.request.user).all()

            for item in items.values():
                orderitem = OrderItem(order=order, menuitem_id=item['menuitem_id'],
                                      price=item['price'], quantity=item['quantity'],
                                      unit_price=item['unit_price'],)
                orderitem.save()
            Cart.objects.all().filter(user=self.request.user).delete()

            result = order_serializer.data.copy()
            result['total'] = total
            return Response(order_serializer.data)
    
    def get_total_price(self, user):
        total = 0
        items = Cart.objects.all().filter(user=user).all()
        for item in items.values():
            total += item['price']
        return total

class SingleOrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    # managers = User.objects.filter(groups__name='Manager')
    # delivery_crew = User.objects.filter(groups__name='Delivery crew')

    # def get_queryset(self):
    #     user = self.request.user
    #     if user in self.managers:
    #         return self.queryset
    #     elif user in self.delivery_crew:
    #         return self.queryset.filter(delivery_crew=user)
    #     else:
    #         return self.queryset.filter(user=user)
    def update(self, request, *args, **kwargs):
        if self.request.user.groups.count() == 0:
            return Response("Not Ok")
        else:
            return super().update(request, *args, **kwargs)