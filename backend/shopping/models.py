from django.db import models
from recipes.models import Recipe
from accounts.models import User
from django.core.validators import MinValueValidator
# Create your models here.

class CartItem(models.Model):

    objects = models.Manager()
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quantity = models.IntegerField(blank=True, default=1, validators=[MinValueValidator(1)])