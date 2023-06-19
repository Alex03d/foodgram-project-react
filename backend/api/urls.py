from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import (UserViewSet, TagViewSet, IngredientViewSet,
                    RecipeViewSet, SubscriptionViewSet, FavoriteViewSet,
                    ShoppingListViewSet)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='users')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'recipes', RecipeViewSet, basename='recipes')
router.register(r'subscriptions', SubscriptionViewSet, basename='subscriptions')
router.register(r'favorites', FavoriteViewSet, basename='favorites')
router.register(r'shopping_lists', ShoppingListViewSet, basename='shopping_lists')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('auth/', include('djoser.urls.jwt')),
]
