from django.db.models import Sum
from django.http import HttpResponse
from rest_framework import mixins, status, viewsets, views
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from recipes.models import Ingredient, Recipe, RecipeIngredient, ShoppingList, Tag
from .serializers import RecipeSerializer


class ShoppingListManipulation(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        recipe = Recipe.objects.get(id=id)
        ShoppingList.objects.get_or_create(user=request.user, recipe=recipe)
        serializer = RecipeSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, id):
        recipe = Recipe.objects.get(id=id)
        item = ShoppingList.objects.filter(user=request.user, recipe=recipe)
        if item.exists():
            item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({"detail": "Recipe not in shopping list."}, status=status.HTTP_400_BAD_REQUEST)


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

    @action(detail=False, methods=["GET"], permission_classes=(IsAuthenticated,), pagination_class=None)
    def download_shopping_cart(self, request):
        shopping_list_recipes = ShoppingList.objects.filter(user=request.user).values_list('recipe', flat=True)
        ingredients = RecipeIngredient.objects.filter(
            recipe__in=shopping_list_recipes
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).order_by(
            'ingredient__name'
        ).annotate(ingredient_total=Sum('amount'))

        return self.convert_txt(ingredients)

    @staticmethod
    def convert_txt(ingredients):
        """Конвертирует список ингредиентов в текстовый файл"""
        response = HttpResponse(content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="ingredients.txt"'

        for ingredient in ingredients:
            line = f"{ingredient['ingredient__name']} - {ingredient['ingredient_total']} {ingredient['ingredient__measurement_unit']}\n"
            response.write(line)

        return response
