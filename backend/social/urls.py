from django.urls import path
from .views import *

urlpatterns = [
    path('<int:recipe_id>/favorite/', RecipeFavoriteView().as_view(), name='like-recipe'),
    path('<int:recipe_id>/unfavorite/', RecipeUnfavoriteView().as_view(), name='unlike-recipe'),
    path('<int:recipe_id>/favorites_count/', RecipeNumFavoritesView.as_view(), name='recipe-likes'),
    path('<int:recipe_id>/rate/', RecipeRateView.as_view(), name='rate'),
    path('<int:recipe_id>/rating_info/', RecipeRatingInfoView.as_view(), name='avg-rating'),
    ]