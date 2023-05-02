from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, UpdateAPIView, DestroyAPIView
from django.db.models import Q, Sum
from recipes.models import Recipe, Ingredient, IngredientName
from .models import CartItem
from .serializers import CartItemSerializer


class RemoveItemView(DestroyAPIView):

    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):

        recipe = get_object_or_404(Recipe, pk=self.kwargs['recipe_id'])
        user = self.request.user
        return get_object_or_404(CartItem, Q(recipe=recipe) & Q(user=user))

class EditQuantityView(UpdateAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):

        recipe = get_object_or_404(Recipe, pk=self.kwargs['recipe_id'])

        user = self.request.user

        data = {"recipe" : recipe, "user" : user}
        item = CartItem.objects.get_or_create(**data)[0]
        return item

class ShoppingCartView(ListAPIView):

    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self, *args, **kwargs):

        queryset = CartItem.objects.filter(user=self.request.user)
        return queryset.order_by('recipe_id')

class ItemizedView(APIView):

    def get(self, request):

        user = request.user
        cart_recipes = CartItem.objects.filter(user=user)
        all_ingredients = Ingredient.objects.filter(recipe=cart_recipes[0].recipe)

        for i in range(1, len(cart_recipes)):
            all_ingredients = all_ingredients.union(Ingredient.objects.filter(recipe=cart_recipes[i].recipe), all=True)

        ingredient_groups = all_ingredients.values_list('ingredient_name', 'units')

        res = []


        for id_, units in ingredient_groups:
            count = 0
            ingredient = IngredientName.objects.get(pk=id_)
            for item in cart_recipes:
                matches = Ingredient.objects.filter(ingredient_name=ingredient, recipe=item.recipe, units=units)
                if matches:
                    count += matches[0].quantity * item.quantity
            res.append((ingredient.name, units, count))

        response = {"result" : res}

        return Response(response, status=200)
