from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (RecipeViewSet, ShoppingListManipulation,
                    TagViewSet, IngredientViewSet)
from .views import UserViewSet as CustomUserViewSet


app_name = 'api'

router = DefaultRouter()
router.register(r'recipes', RecipeViewSet, basename='recipe')
router.register(r'tags', TagViewSet, basename='tag')
router.register(r'users', CustomUserViewSet, basename='user')
router.register(r'ingredients', IngredientViewSet, basename='ingredient')


urlpatterns = [
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
    path('recipes/<int:id>/shopping_cart/',
         ShoppingListManipulation.as_view()),
]
