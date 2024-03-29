from django.db.models import Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status, views, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingList, Tag)
from users.models import User, Subscription
from .filters import IngredientFilter, RecipeFilter
from .paginations import CustomPagination
from .permissions import IsOwnerOrReadOnly
from .serializers import (IngredientSerializer, RecipeSerializer,
                          RecipeShortSerializer, SubscriptionSerializer,
                          TagSerializer, MyUserSerializer,
                          RecipeUpdateSerializer)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = MyUserSerializer

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=(IsAuthenticated,))
    def subscribe(self, request, pk=None):
        user = self.get_object()
        subscriber = request.user
        if user != subscriber:
            if request.method == 'POST':
                subscription, created = Subscription.objects.get_or_create(
                    user=subscriber,
                    author=user
                )
                if created:
                    serializer = MyUserSerializer(
                        user,
                        context={'request': request}
                    )
                    return Response(
                        serializer.data,
                        status=status.HTTP_201_CREATED
                    )
                else:
                    return Response(
                        {"detail": "Already subscribed."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            elif request.method == 'DELETE':
                subscription = Subscription.objects.get(
                    user=subscriber,
                    author=user
                )
                subscription.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(
                {"detail": "Though cannot subscribe to yourself."},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(
        detail=False,
        methods=["GET"],
        permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request):
        subscriptions = Subscription.objects.filter(user=request.user)
        paginator = PageNumberPagination()
        paginator.page_size = 10
        result_page = paginator.paginate_queryset(subscriptions, request)
        serializer = SubscriptionSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    @action(
        detail=False,
        methods=["GET"],
        permission_classes=(IsAuthenticated,)
    )
    def me(self, request):
        serializer = MyUserSerializer(
            request.user,
            context={'request': request})
        return Response(serializer.data)

    @action(
        detail=False,
        methods=['post'],
        permission_classes=[IsAuthenticated])
    def set_password(self, request):
        print('Начинаем')
        user = request.user  # Получение текущего пользователя
        if 'new_password' not in request.data:
            return Response(
                {"new_password": ["This field is required."]},
                status=status.HTTP_400_BAD_REQUEST)

        password = request.data['new_password']
        user.set_password(password)
        user.save()
        print('Кончаем')
        return Response(status=status.HTTP_204_NO_CONTENT)


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
        return Response(
            {"detail": "Recipe not in shopping list."},
            status=status.HTTP_400_BAD_REQUEST
        )


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = CustomPagination
    permission_classes = (IsOwnerOrReadOnly,)

    def get_permissions(self):
        if self.request.method == 'POST':
            self.permission_classes = (IsAuthenticated,)
        return super(RecipeViewSet, self).get_permissions()

    def create(self, request, *args, **kwargs):
        data = request.data
        serializer = RecipeSerializer(
            data=data,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        recipe = self.get_object()
        data = request.data
        serializer = RecipeUpdateSerializer(   # заменили на новый сериализатор
            recipe,
            data=data,
            # partial=True,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["GET"],
            permission_classes=(IsAuthenticated,),
            pagination_class=None)
    def download_shopping_cart(self, request):
        shopping_cart_recipes = ShoppingList.objects.filter(
            user=request.user).values_list('recipe', flat=True
                                           )
        ingredients = RecipeIngredient.objects.filter(
            recipe__in=shopping_cart_recipes
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).order_by(
            'ingredient__name'
        ).annotate(ingredient_total=Sum('amount'))

        return self.convert_txt(ingredients)

    @staticmethod
    def convert_txt(ingredients):
        response = HttpResponse(content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename="ingredients.txt"'
        )

        for ingredient in ingredients:
            line = (
                f"{ingredient['ingredient__name']} - "
                f"{ingredient['ingredient_total']} "
                f"{ingredient['ingredient__measurement_unit']}\n"
            )
            response.write(line)

        return response

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        recipe = self.get_object()
        user = request.user
        favorite = Favorite.objects.filter(user=user, recipe=recipe)

        if request.method == 'POST':
            if favorite.exists():
                return Response(status=status.HTTP_400_BAD_REQUEST)
            else:
                Favorite.objects.create(user=user, recipe=recipe)
                serializer = RecipeShortSerializer(recipe)
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED
                )
        elif request.method == 'DELETE':
            if favorite.exists():
                favorite.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(
                    {"detail": "Recipe not in favorites."},
                    status=status.HTTP_400_BAD_REQUEST
                )


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для  тегов: ReadOnly."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.AllowAny, )
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для  рецептов: ReadOnly."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (permissions.AllowAny, )
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    pagination_class = None
