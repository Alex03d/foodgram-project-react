from django.shortcuts import get_object_or_404
from django.views import View
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from recipes.models import Recipe, FavoriteRecipe, ShoppingList
from .serializers import RecipeSerializer, ShoppingListSerializer


class FavoriteListView(generics.ListAPIView):
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Recipe.objects.filter(favorite_recipes__user=self.request.user)


class FavoriteAddView(View):
    permission_classes = [IsAuthenticated]

    def post(self, request, recipe_id):
        recipe = get_object_or_404(Recipe, id=recipe_id)
        FavoriteRecipe.objects.get_or_create(user=request.user, recipe=recipe)
        return Response({'status': 'added to favorites'})


class FavoriteDeleteView(View):
    permission_classes = [IsAuthenticated]

    def post(self, request, recipe_id):
        recipe = get_object_or_404(Recipe, id=recipe_id)
        FavoriteRecipe.objects.filter(user=request.user, recipe=recipe).delete()
        return Response({'status': 'removed from favorites'})


class ShoppingListView(generics.ListAPIView):
    serializer_class = ShoppingListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ShoppingList.objects.filter(user=self.request.user)


class ShoppingAddView(View):
    permission_classes = [IsAuthenticated]

    def post(self, request, recipe_id):
        recipe = get_object_or_404(Recipe, id=recipe_id)
        ShoppingList.objects.get_or_create(user=request.user, recipe=recipe)
        return Response({'status': 'added to shopping list'})


class ShoppingDeleteView(View):
    permission_classes = [IsAuthenticated]

    def post(self, request, recipe_id):
        recipe = get_object_or_404(Recipe, id=recipe_id)
        ShoppingList.objects.filter(user=request.user, recipe=recipe).delete()
        return Response({'status': 'removed from shopping list'})


class ShoppingDownloadView(View):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # TODO: implement this function
        pass


class TaggedRecipesView(generics.ListAPIView):
    serializer_class = RecipeSerializer

    def get_queryset(self):
        tag_slug = self.kwargs['tag_slug']
        return Recipe.objects.filter(tags__slug=tag_slug)
