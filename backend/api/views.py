from rest_framework import viewsets, permissions
from rest_framework.exceptions import PermissionDenied
from .serializers import RecipeSerializer, RecipeUpdateSerializer, UserCreateSerializer, UserSerializer
from recipes.models import Recipe
from django.contrib.auth import get_user_model

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return RecipeUpdateSerializer
        return RecipeSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.author != request.user:
            raise PermissionDenied("You can't update this recipe")
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.author != request.user:
            raise PermissionDenied("You can't delete this recipe")
        return super().destroy(request, *args, **kwargs)



# from django.shortcuts import get_object_or_404
# from django.views import View
# from rest_framework import generics
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.response import Response
# from rest_framework.views import APIView
#
# from recipes.models import Recipe, FavoriteRecipe, ShoppingList, Ingredient
# from .serializers import RecipeSerializer, ShoppingListSerializer, IngredientSerializer
#
#
# class RecipeView(generics.ListCreateAPIView):
#     queryset = Recipe.objects.all()
#     serializer_class = RecipeSerializer
#
#
# class FavoriteListView(generics.ListAPIView):
#     serializer_class = RecipeSerializer
#     permission_classes = [IsAuthenticated]
#
#     def get_queryset(self):
#         return Recipe.objects.filter(favorite_recipes__user=self.request.user)
#
#
# class FavoriteAddView(View):
#     permission_classes = [IsAuthenticated]
#
#     def post(self, request, recipe_id):
#         recipe = get_object_or_404(Recipe, id=recipe_id)
#         FavoriteRecipe.objects.get_or_create(user=request.user, recipe=recipe)
#         return Response({'status': 'added to favorites'})
#
#
# class FavoriteDeleteView(View):
#     permission_classes = [IsAuthenticated]
#
#     def post(self, request, recipe_id):
#         recipe = get_object_or_404(Recipe, id=recipe_id)
#         FavoriteRecipe.objects.filter(user=request.user, recipe=recipe).delete()
#         return Response({'status': 'removed from favorites'})
#
#
# class ShoppingListView(generics.ListAPIView):
#     serializer_class = ShoppingListSerializer
#     permission_classes = [IsAuthenticated]
#
#     def get_queryset(self):
#         return ShoppingList.objects.filter(user=self.request.user)
#
#
# class ShoppingAddView(View):
#     permission_classes = [IsAuthenticated]
#
#     def post(self, request, recipe_id):
#         recipe = get_object_or_404(Recipe, id=recipe_id)
#         ShoppingList.objects.get_or_create(user=request.user, recipe=recipe)
#         return Response({'status': 'added to shopping list'})
#
#
# class ShoppingDeleteView(View):
#     permission_classes = [IsAuthenticated]
#
#     def post(self, request, recipe_id):
#         recipe = get_object_or_404(Recipe, id=recipe_id)
#         ShoppingList.objects.filter(user=request.user, recipe=recipe).delete()
#         return Response({'status': 'removed from shopping list'})
#
#
# class ShoppingDownloadView(View):
#     permission_classes = [IsAuthenticated]
#
#     def get(self, request):
#         # TODO: implement this function
#         pass
#
#
# class TaggedRecipesView(generics.ListAPIView):
#     serializer_class = RecipeSerializer
#
#     def get_queryset(self):
#         tag_slug = self.kwargs['tag_slug']
#         return Recipe.objects.filter(tags__slug=tag_slug)
#
#
# # class IngredientList(APIView):
# #     def get(self, request):
# #         ingredients = Ingredient.objects.all()
# #         serializer = IngredientSerializer(ingredients, many=True)
# #         return Response(serializer.data)
#
# class IngredientView(generics.ListCreateAPIView):
#     queryset = Ingredient.objects.all()
#     serializer_class = IngredientSerializer
