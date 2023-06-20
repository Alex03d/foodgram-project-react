from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from recipes.models import Recipe, Tag, Ingredient, RecipeIngredient
from .serializers import RecipeSerializer, IngredientSerializer, RecipeIngredientSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            self.permission_classes = (IsAuthenticated,)
        return super(RecipeViewSet, self).get_permissions()

    def create(self, request, *args, **kwargs):
        data = request.data
        serializer = RecipeSerializer(data=data, context={'request': request})  # Добавлен контекст
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        recipe = self.get_object()
        data = request.data
        serializer = RecipeSerializer(recipe, data=data, context={'request': request})  # Добавлен контекст
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# class RecipeViewSet(viewsets.ModelViewSet):
#     queryset = Recipe.objects.all()
#     serializer_class = RecipeSerializer
#
#     def get_permissions(self):
#         if self.request.method == 'POST':
#             self.permission_classes = (IsAuthenticated,)
#         return super(RecipeViewSet, self).get_permissions()
#
#     def create(self, request, *args, **kwargs):
#         data = request.data
#         data['author'] = request.user.id
#         recipe = RecipeSerializer(data=data)
#         if recipe.is_valid():
#             recipe.save()
#             return Response(recipe.data, status=status.HTTP_201_CREATED)
#         return Response(recipe.errors, status=status.HTTP_400_BAD_REQUEST)
#
#     def update(self, request, *args, **kwargs):
#         recipe = self.get_object()
#         data = request.data
#         data['author'] = request.user.id
#         serializer = RecipeSerializer(recipe, data=data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class IngredientsViewSet(viewsets.ModelViewSet):
    pass


class SubscriptionViewSet(viewsets.ModelViewSet):
    pass


class SubscribeView(viewsets.ModelViewSet):
    pass


class TagsViewSet(viewsets.ModelViewSet):
    pass
