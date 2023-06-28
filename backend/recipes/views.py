from rest_framework import viewsets

from .models import (FavoriteRecipe, Follow, Ingredient, IngredientAmount,
                     Recipe, ShoppingList, Tag)
from .serializers import (FavoriteRecipeSerializer, FollowSerializer,
                          IngredientAmountSerializer, IngredientSerializer,
                          RecipeSerializer, ShoppingListSerializer,
                          TagSerializer)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer


class IngredientAmountViewSet(viewsets.ModelViewSet):
    queryset = IngredientAmount.objects.all()
    serializer_class = IngredientAmountSerializer


class FavoriteRecipeViewSet(viewsets.ModelViewSet):
    queryset = FavoriteRecipe.objects.all()
    serializer_class = FavoriteRecipeSerializer


class ShoppingListViewSet(viewsets.ModelViewSet):
    queryset = ShoppingList.objects.all()
    serializer_class = ShoppingListSerializer


class FollowViewSet(viewsets.ModelViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
