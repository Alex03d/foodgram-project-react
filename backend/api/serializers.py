import base64
import uuid

from rest_framework import serializers
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


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')

    def __str__(self):
        return f'{self.ingredient} in {self.recipe}'

# class RecipeIngredientSerializer(serializers.ModelSerializer):
#     id = serializers.IntegerField(source='ingredient.id')
#     amount = serializers.IntegerField()
#
#     class Meta:
#         model = RecipeIngredient
#         fields = ('id', 'amount',)
#
#     def validate_id(self, value):
#         if not Ingredient.objects.filter(id=value).exists():
#             raise serializers.ValidationError('Ингредиент не существует')
#         return value
#
#     def create(self, validated_data):
#         ingredient_id = validated_data['ingredient']['id']
#         ingredient = Ingredient.objects.get(id=ingredient_id)
#         amount = validated_data['amount']
#         return RecipeIngredient.objects.create(ingredient=ingredient, amount=amount)
#
#     def update(self, instance, validated_data):
#         if 'ingredient' in validated_data:
#             ingredient_id = validated_data['ingredient']['id']
#             instance.ingredient = Ingredient.objects.get(id=ingredient_id)
#         if 'amount' in validated_data:
#             instance.amount = validated_data['amount']
#         instance.save()
#         return instance


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
    # ingredients = RecipeIngredientSerializer(
    #     many=True,
    #     source='ingredients'
    # )
    image = Base64ImageField(
        max_length=None, use_url=True,
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = '__all__'

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

        user = self.context['request'].user if 'request' in self.context and self.context[
            'request'].user.is_authenticated else None
        print(user)

        if not user or not user.is_authenticated:
            raise serializers.ValidationError("Authentication is fucking required to create a recipe.")

        recipe = Recipe.objects.create(author=user, **validated_data)

        for tag in tags_data:
            recipe.tags.add(tag)

        for ingredient_data in ingredients_data:
            print(ingredient_data)
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=Ingredient.objects.get(
                    id=ingredient_data['id']
                ),
                amount=ingredient_data['amount']
            )

        recipe.save()
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('recipeingredients')
        tags_data = validated_data.pop('tags')

        Recipe.objects.filter(id=instance.id).update(**validated_data)

        instance.recipeingredients.all().delete()

        for ingredient_data in ingredients_data:
            RecipeIngredient.objects.create(recipe=instance, **ingredient_data)

        instance.tags.clear()
        for tag in tags_data:
            instance.tags.add(tag.id)  # Заменил tag_data на tag.id

        return instance







