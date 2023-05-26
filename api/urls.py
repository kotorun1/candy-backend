from django.urls import path
from .views import SignUpApi, LoginApi, LogoutApi, ProductApi, CartApi, OrderApi, CartDetail

urlpatterns = [
    path('signup', SignUpApi.as_view()),
    path('login', LoginApi.as_view()),
    path('logout', LogoutApi.as_view()),

    path('products', ProductApi.as_view({'get': 'list'})),
    path('product/<int:pk>', ProductApi.as_view({'delete': 'destroy', 'patch': 'update'})),
    path('product', ProductApi.as_view({'post': 'create'})),

    path('cart/<int:pk>', CartDetail.as_view()),
    path('cart', CartApi.as_view()),

    path('order', OrderApi.as_view())
]