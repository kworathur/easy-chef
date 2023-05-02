from django.urls import path
from .views import *


urlpatterns = [
path('edit/<int:recipe_id>/', EditQuantityView.as_view(), name='edit-quantity'),
    path('remove/<int:recipe_id>/', RemoveItemView.as_view(), name='remove-item'),
    path('cart/', ShoppingCartView.as_view(), name='recipe-likes'),
    path('cart/ingredients/', ItemizedView.as_view(), name='itemized-view'),
    ]