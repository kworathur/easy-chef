from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.generics import UpdateAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from recipes.models import Recipe
from .models import RatingRecord
from .serializers import RatingRecordSerializer

# Create your views here.
class RecipeFavoriteView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, **kwargs):

        recipe = get_object_or_404(Recipe, pk=self.kwargs['recipe_id'])
        if recipe.creator == self.request.user:
            return Response({"error" : "user cannot like their own recipe."}, status=409)
        recipe.liked_by.add(self.request.user)
        recipe.save()
        data = {"favorites": len(recipe.liked_by.all())}
        return Response({"favorites" : len(recipe.liked_by.all())}, status=200)

class RecipeUnfavoriteView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, **kwargs):

        recipe = get_object_or_404(Recipe, pk=kwargs['recipe_id'])
        recipe.liked_by.remove(self.request.user)
        recipe.save()
        data = {"favorites" : len(recipe.liked_by.all())}
        return Response(data, status=200)

class RecipeNumFavoritesView(APIView):

    def get(self, request, **kwargs):

        recipe = get_object_or_404(Recipe, pk=kwargs['recipe_id'])
        data = {"favorites" : len(recipe.liked_by.all())}
        return Response(data, status=200)

class RecipeRateView(UpdateAPIView):

    serializer_class = RatingRecordSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self, *args, **kwargs):
        recipe = get_object_or_404(Recipe, pk=self.kwargs['recipe_id'])
        user = self.request.user
        if recipe.creator == user:
            return Response({"error" : "User cannot rate their own recipe"}, status=409)

        data = {"recipe": recipe, "user" : user}
        record = RatingRecord.objects.get_or_create(**data)[0]
        return record

class RecipeRatingInfoView(APIView):

    def get(self, request, **kwargs):

        recipe = get_object_or_404(Recipe, pk=self.kwargs['recipe_id'])

        if len(recipe.rated_by.all()) == 0:
            return Response({"rating" : 0})

        total_points = 0

        for record in RatingRecord.objects.filter(recipe=recipe):
            total_points += record.rating

        data = {"rating" : total_points // len(recipe.rated_by.all())}

        return Response(data, status=200)