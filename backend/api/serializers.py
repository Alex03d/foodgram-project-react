import base64
import uuid

from rest_framework import serializers
# from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from recipes.models import Recipe, Tag, Ingredient, RecipeIngredient
from users.models import User


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            id = uuid.uuid4()
            data = ContentFile(base64.b64decode(imgstr), name=id.urn[9:]+'.'+ext)
        return super().to_internal_value(data)


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.BooleanField(default=False)

    class Meta:
        model = User
        fields = ['email', 'id', 'username', 'first_name', 'last_name', 'is_subscribed']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'color', 'slug']
        read_only_fields = ['id']


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'measurement_unit']


# class RecipeIngredientSerializer(serializers.ModelSerializer):
#     id = serializers.IntegerField(source='ingredient.id')
#     amount = serializers.IntegerField()
#
#     class Meta:
#         model = RecipeIngredient
#         fields = ['id', 'amount']


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """
    Сериализатор ингердиентов в рецепте
    """
    id = serializers.IntegerField()
    # id = serializers.ReadOnlyField(source='ingredient.id')
    # amount = serializers.ReadOnlyField(source='ingredient.amount')

    # name = serializers.ReadOnlyField(source='ingredient.name')
    # measurement_unit = serializers.ReadOnlyField(
    #     source='ingredient.measurement_unit'
    # )

    # validators = (
    #     UniqueTogetherValidator(
    #         queryset=IngredientInRecipe.objects.all(),
    #         fields=('ingredient', 'recipe')
    #     ),
    # )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')

    def __str__(self):
        return f'{self.ingredient} in {self.recipe}'


class RecipeSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        many=True,
        source='recipeingredients'
    )
    image = Base64ImageField(
        max_length=None, use_url=True,
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = '__all__'
        # fields = ['id', 'tags', 'author', 'ingredients', 'is_favorited',
        #           'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time']

    def get_is_favorited(self, obj):
        pass

    def get_is_in_shopping_cart(self, obj):
        pass

    def create(self, validated_data):
        try:
            tags_data = validated_data.pop('tags')
            ingredients_data = validated_data.pop('recipeingredients')
        except KeyError as e:
            raise serializers.ValidationError(
                f"Отсутствуют необходимые данные: {str(e)}"
            )

        # Check if 'request' is in context and get the user
        # user = self.context['request'].user if 'request' in self.context else None
        # user = self.context['request'].user if 'request' in self.context and self.context[
        #     'request'].user.is_authenticated else None
        user = self.context['request'].user if 'request' in self.context and self.context[
            'request'].user.is_authenticated else None
        print(user)

        # If there's no user in the request or user is not authenticated,
        # raise a validation error
        if not user or not user.is_authenticated:
            raise serializers.ValidationError("Authentication is fucking required to create a recipe.")

        recipe = Recipe.objects.create(author=user, **validated_data)

        # for tag_id in tags_data:
        #     tag = Tag.objects.get(id=tag_id)
        #     recipe.tags.add(tag)
        for tag in tags_data:
            recipe.tags.add(tag)

        for ingredient_data in ingredients_data:
            print(ingredient_data)
            RecipeIngredient.objects.create(
                recipe=recipe,
                # ingredient=Ingredient.objects.get(
                #     id=ingredient_data['ingredient']['id']
                # ),
                ingredient=Ingredient.objects.get(
                    id=ingredient_data['id']
                ),
                amount=ingredient_data['amount']
            )

        recipe.save()
        return recipe

    # def create(self, validated_data):
    #     tags_data = validated_data.pop('tags')
    #     ingredients_data = validated_data.pop('ingredients')
    #     recipe = Recipe.objects.create(**validated_data)
    #     for tag_id in tags_data:
    #         tag = Tag.objects.get(id=tag_id)
    #         recipe.tags.add(tag)
    #     for ingredient_data in ingredients_data:
    #         RecipeIngredient.objects.create(
    #             recipe=recipe,
    #             ingredient=Ingredient.objects.get(
    #                 id=ingredient_data['ingredient']['id']
    #             ),
    #             amount=ingredient_data['amount']
    #         )
    #     recipe.save()
    #     return recipe
