from django.urls import path

from .views import (
    FavoriteListView,
    FavoriteAddView,
    FavoriteDeleteView,
    ShoppingListView,
    ShoppingAddView,
    ShoppingDeleteView,
    ShoppingDownloadView,
    TaggedRecipesView,
)

urlpatterns = [
    path('favorites/', FavoriteListView.as_view(), name='favorite_list'),
    path('favorites/add/<int:recipe_id>/', FavoriteAddView.as_view(), name='favorite_add'),
    path('favorites/delete/<int:recipe_id>/', FavoriteDeleteView.as_view(), name='favorite_delete'),
    path('shopping_list/', ShoppingListView.as_view(), name='shopping_list'),
    path('shopping_list/add/<int:recipe_id>/', ShoppingAddView.as_view(), name='shopping_list_add'),
    path('shopping_list/delete/<int:recipe_id>/', ShoppingDeleteView.as_view(), name='shopping_list_delete'),
    path('shopping_list/download/', ShoppingDownloadView.as_view(), name='shopping_list_download'),
    path('tags/<slug:tag_slug>/', TaggedRecipesView.as_view(), name='tagged_recipes'),
]
