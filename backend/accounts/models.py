from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import UserManager
# Create your models here.
class User(AbstractUser):
    # Profile information should include first and last name, email, avatar, and phone number.
    first_name = models.CharField(max_length=100, blank=False, null=False)
    last_name = models.CharField(max_length=100, blank=False, null=False)
    email = models.EmailField(blank=False, null=False, unique=True)
    avatar = models.ImageField(upload_to="user_avatars/", blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    username = None

    objects = UserManager()

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return "{}".format( self.email)