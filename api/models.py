from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser
from django.db import models


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, fio, email, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        if not email:
            raise ValueError("The given username must be set")
        email = self.normalize_email(email)
        user = self.model(fio=fio, email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, fio, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(fio, email, password, **extra_fields)

    def create_superuser(self, fio, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(fio, email, password, **extra_fields)


class User(AbstractUser):
    fio = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=50, blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('fio', )
    objects = UserManager()


class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    img = models.URLField(max_length=200)
    price = models.IntegerField()



class Cart(models.Model):
    products = models.ManyToManyField(Product, )
    user = models.OneToOneField(User, on_delete=models.CASCADE)


class Order(models.Model):
    products = models.ManyToManyField(Cart, )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order_price = models.IntegerField(default=0)
