from django.contrib.auth import authenticate
from .models import User, Product, Cart, Order
from rest_framework import serializers


class LoginSerializers(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, attrs):
        user = authenticate(**attrs)
        if user:
            return user
        return False


class SignUpSerializers(serializers.ModelSerializer):
    email = serializers.EmailField()
    fio = serializers.CharField()
    password = serializers.CharField()

    class Meta:
        model = User
        fields = '__all__'

    def save(self, **kwargs):
        user = User(
            fio=self.validated_data['fio'],
            email=self.validated_data['email']
        )
        user.set_password(self.validated_data['password'])
        user.save()
        return user


class ProductSerializers(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class CartSerializers(serializers.ModelSerializer):
    products = ProductSerializers(many=True)

    class Meta:
        model = Cart
        fields = '__all__'


class OrderSerializers(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'

