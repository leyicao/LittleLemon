from rest_framework import serializers
from django.contrib.auth.models import User
from .models import MenuItem, Category, Order, Cart, OrderItem
from decimal import *

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'title', 'slug']

        def __str__(self) -> str:
            return self.title

class MenuItemSerializer(serializers.ModelSerializer):
    # category_id = serializers.IntegerField(write_only=True)
    # category = CategorySerializer(read_only=True)
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'price', 'featured', 'category', 'featured']

class UserSerializer(serializers.ModelSerializer):
    # class Meta:
    #     model = User
    #     fields = ['id', 'username', 'password', 'groups']
    #     extra_kwargs = {'password': {'write_only': True}}

    #     def create(self, validated_data):
    #         groups_data = validated_data.pop('groups')
    #         user = User.objects.create(**validated_data)
    #         for group_data in groups_data:
    #             user.groups.add(group_data)
    #         return user
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class CartSerializer(serializers.ModelSerializer):
    # item = serializers.CharField(source='menuitem.title', read_only=True)
    # unit_price = serializers.DecimalField(max_digits=6, decimal_places=2, source='menuitem.price', read_only=True)
    # class Meta:
    #     model = Cart
    #     fields = ['item', 'menuitem', 'unit_price', 'quantity', 'price']
    #     extra_kwargs = {
    #         'price' : {'read_only': True},
    #         'menuitem': {'write_only': True},
    #     }
    
    # def total_price(self, obj):
    #     item = MenuItemSerializer(MenuItem.objects.get(title=obj.menuitem))
    #     return Decimal(item.data.get('price')) * obj.quantity
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), default=serializers.CurrentUserDefault())

    def validate(self, attrs):
        attrs['price'] = attrs['quantity'] * attrs['unit_price']
        return attrs
    
    class Meta:
        model = Cart
        fields = ['user', 'menuitem', 'unit_price', 'quantity', 'price']
        extra_kwargs = {
            'price' : {'read_only': True},
        }
        
class OrderItemSerializer(serializers.ModelSerializer):
    # item = serializers.CharField(source='menuitem.title', read_only=True)
    # unit_price = serializers.DecimalField(max_digits=6, decimal_places=2, source='menuitem.price', read_only=True)
    # class Meta:
    #     model = OrderItem
    #     fields = ['menuitem', 'item', 'unit_price', 'quantity', 'price']
    #     extra_kwargs = {
    #         'price' : {'read_only': True},
    #     }
    class Meta:
        model = OrderItem
        fields = ['order', 'menuitem', 'quantity', 'price']

class OrderSerializer(serializers.ModelSerializer):
    order_items = serializers.SerializerMethodField(method_name = 'get_order_items')
    class Meta:
        model = Order
        fields = ['id', 'user', 'delivery_crew', 'status', 'total', 'date', 'order_items']
        extra_kwargs = {
            'total' : {'read_only': True},
        }
    
    def get_order_items(self, obj):
        order_items = OrderItem.objects.filter(order=obj)
        serializers = OrderItemSerializer(order_items, many=True, context={'request': self.context['request']})
        return serializers.data
    # orderitem = OrderItemSerializer(many=True, read_only=True, source='order')

    # class Meta:
    #     model = Order
    #     fields = ['id', 'user', 'delivery_crew', 'status', 'date', 'total', 'orderitem']
