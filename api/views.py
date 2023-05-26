from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from .serializers import ProductSerializers, CartSerializers, OrderSerializers, SignUpSerializers, LoginSerializers
from .models import Product, Cart, Order, User
from .authentication import BearerAuthentication
from .permission import IsAdminOrReadOnly


class ProductApi(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializers
    permission_classes = [IsAdminOrReadOnly, ]

    def create(self, request, *args, **kwargs):
        serializer = ProductSerializers(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({"data": {'id': serializer.data['id'], "messages": "product add"}}, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"data": {"messages": "product removed"}}, status=status.HTTP_204_NO_CONTENT)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class LoginApi(APIView):
    authentication_classes = (BearerAuthentication, )
    permission_classes = ()

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializers(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({"data": {'user_token': token.key}})
        return Response({"error": {"code": "401", "message": "Authentication failed"}})


class SignUpApi(APIView):
    authentication_classes = (BearerAuthentication,)
    permission_classes = ()

    def post(self, request, *args, **kwargs):
        serializer = SignUpSerializers(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token = Token.objects.create(user=user)
            return Response({"data": {'user_token': token.key}})
        return Response({"error": {"code": "422", "message": "validation errors", "errors": serializer.errors}})


class LogoutApi(APIView):
    authentication_classes = (BearerAuthentication, )
    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        request.user.auth_token.delete()
        return Response({"data": {"messages": "logout"}})


class CartApi(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart, new_cart = Cart.objects.get_or_create(user=request.user)
        return Response({"data": CartSerializers(cart, many=False).data['products']}, status.HTTP_200_OK)


class CartDetail(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, **kwargs):
        try:
            product = Product.objects.get(pk=kwargs['pk'])
        except:
            return Response({"error": {"code": "404", "messages": "Not Found"}})
        cart, new_cart = Cart.objects.get_or_create(user=request.user)
        cart.products.add(product)
        return Response({"data": {"messages": "Product add to card"}}, status=status.HTTP_201_CREATED)

    def delete(self, request, **kwargs):
        try:
            product = Product.objects.get(pk=kwargs['pk'])
        except:
            return Response({"error": {"code": "404", "messages": "Not Found"}})
        cart, new_cart = Cart.objects.get_or_create(user=request.user)
        cart.products.delete(product)
        return Response({"data": {"messages": "Item removed from cart"}}, status=status.HTTP_201_CREATED)


class OrderApi(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            cart = Cart.objects.get(user=request.user)
        except:
            return Response({"error": {"code": "422", "messages": "Cart is empty"}}, status=422)
        order = Order(user=request.user)
        price = 0
        for product in cart.products.all():
            price += product.price
        order.order_price = price
        order.save()
        for product in cart.products.all():
            order.products.add(product)
        order.save()
        cart.delete()
        return Response({"data": {"order_id": order.id, "message": "Order is processed"}}, status=status.HTTP_201_CREATED)

    def get(self, request):
        order = Order.objects.filter(user=request.user)
        return Response({"data": OrderSerializers(order, many=True).data}, status.HTTP_200_OK)









