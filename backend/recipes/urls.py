from django.urls import path
from .views import *


urlpatterns = [
    path('add/', RecipeCreationView.as_view(), name='add'),
    path('media/upload/', MediaUploadView.as_view(), name='upload-media'),
    path('ingredient/matches/', IngredientAutocompleteView.as_view(), name='ingredient-autocomplete'),
    path('ingredient/create/', IngredientNameCreateView.as_view(), name='ingredient-create'),
    path('<int:recipe_id>/delete/', RecipeDeletionView.as_view(), name='delete'),
    path('<int:recipe_id>/edit/', RecipeEditView.as_view(), name='edit'),
    path('<int:recipe_id>/details/', RecipeDetailView.as_view(), name='details'),
    path('search/', RecipeResultsView.as_view(), name='search'),
    # API endpoints to service comment functionality
    path('<int:recipe_id>/comments/all/', CommentListView.as_view(), name='all-comments'),
    path('<int:recipe_id>/comments/new/', CommentCreateView.as_view(), name='new-comment'),
    path('<int:recipe_id>/comments/<int:comment_id>/edit/', CommentUpdateView.as_view(), name='edit-comment'),

]