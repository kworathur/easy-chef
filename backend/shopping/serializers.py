from rest_framework import serializers
from .models import CartItem
from recipes.serializers import RecipeSerializer


class CartItemSerializer(serializers.ModelSerializer):

    recipe = RecipeSerializer(read_only=True)

    class Meta:
        model = CartItem
        fields = ['recipe', 'quantity']


    def update(self, instance, validated_data):
        instance.quantity = validated_data.get('quantity', instance.quantity)
        instance.save()
        return instance




