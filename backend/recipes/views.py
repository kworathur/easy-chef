from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, UpdateAPIView, DestroyAPIView, RetrieveAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializers import RecipeSerializer, MediaUploadSerializer, CommentSerializer, IngredientNameSerializer
from .models import Recipe, Comment, Diet, IngredientName
from accounts.models import User
from django.db.models import Count, Value
from django.db.models.functions import Concat

# Create your views here.
class IngredientAutocompleteView(APIView):

    def get(self, request):

        matched_ingredients = IngredientName.objects.filter(name__startswith=request.query_params.get('ingredient'))
        data = {"matches" : [ingredient.name for ingredient in matched_ingredients]}
        return Response(data, status=200)

class IngredientNameCreateView(CreateAPIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = IngredientNameSerializer(
            data={"name" : request.data['name']}
        )
        if not serializer.is_valid():
            ingredient_name = IngredientName.objects.get(name=request.data['name'])
            return Response(IngredientNameSerializer(ingredient_name).data, status=409)
        else:
            serializer.save()
            return Response(serializer.data, status=201)

class CommentCreateView(CreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        recipe = Recipe.objects.get(pk=self.kwargs['recipe_id'])
        context.update({"user": self.request.user, "recipe": recipe})
        return context

class CommentUpdateView(UpdateAPIView):

    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return get_object_or_404(Comment, pk=self.kwargs['comment_id'])

class CommentListView(ListAPIView):

    serializer_class = CommentSerializer

    def get_queryset(self, *args, **kwargs):
        recipe = Recipe.objects.get(pk=kwargs['recipe_id'])
        # only select the comments which started their threads
        queryset = Comment.objects.filter(recipe=recipe).filter(reply_to__isnull=True).order_by('-last_edited')
        return queryset

    def list(self, *args, **kwargs):
        queryset = self.get_queryset(**kwargs)
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class RecipeDetailView(RetrieveAPIView):
    serializer_class = RecipeSerializer

    def get_object(self):
        return get_object_or_404(Recipe, pk=self.kwargs['recipe_id'])

class MediaUploadView(CreateAPIView):

    serializer_class = MediaUploadSerializer
    permission_classes = [IsAuthenticated]

class RecipeCreationView(CreateAPIView):

    serializer_class = RecipeSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"user": self.request.user})
        return context

class RecipeDeletionView(DestroyAPIView):

    serializer_class = RecipeSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return get_object_or_404(Recipe, pk=self.kwargs['recipe_id'])

class RecipeEditView(UpdateAPIView):

    serializer_class = RecipeSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return get_object_or_404(Recipe, pk=self.kwargs['recipe_id'])

class RecipeResultsView(ListAPIView):

    serializer_class = RecipeSerializer

    def get_queryset(self):
        search_results = Recipe.objects.all()
        list_type = self.request.query_params.get('list')

        if list_type:
            match list_type:
                case "favorites":
                    return self.request.user.recipes_liked.all()
                case "created":
                    return self.request.user.recipes.all()
                case "interacted":
                    user = self.request.user
                    return user.recipes.all() | \
                           user.recipes_rated.all() | \
                           user.recipes_liked.all()


        name = self.request.query_params.get('name')
        cuisine = self.request.query_params.get('cuisine')
        creator = self.request.query_params.get('creator')
        diet_names = self.request.query_params.getlist('diet[]')
        max_prep_time = self.request.query_params.get('preptime')

        # filter for recipe names matching recipe name
        if name:
            search_results = search_results.filter(name__icontains=name)

        # if cuisine :  filter for recipe names matching cuisine
        if cuisine:
            search_results = search_results.filter(cuisine__icontains=cuisine)

        if creator:
            full_names = User.objects.annotate(full_name=Concat('first_name', Value(' '), 'last_name'))
            matched_user_ids = [creator.id for creator in
                            full_names.filter(full_name__contains=creator)]
            search_results = search_results.filter(creator_id__in=matched_user_ids)

        if diet_names:
            print(diet_names)
            diets = Diet.objects.all()
            for diet_name in diet_names:
                diets = diets.filter(diet__contains=diet_name)

            tagged_with_diet = set()
            for i in range(len(diets)):
                tagged_with_diet.union([recipe.id for recipe in diets[i].recipe_set])

            search_results = search_results.filter(id__in=tagged_with_diet)

        if max_prep_time:
            search_results = search_results.filter(prep_time__lte=max_prep_time)

        # Return final queryset, ordered by number of likes
        search_results = search_results.annotate(likes_count=Count('liked_by')).order_by('-likes_count')

        return search_results

    def post(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
