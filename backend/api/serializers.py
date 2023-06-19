from rest_framework import serializers
from django.contrib.auth import get_user_model
from recipes.models import Recipe, Ingredient, Tag, RecipeIngredient, Subscription, Favorite, ShoppingList, RecipeTag
from drf_extra_fields.fields import Base64ImageField
from django.core.exceptions import ObjectDoesNotExist

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'first_name', 'last_name']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'amount']


class RecipeTagSerializer(serializers.ModelSerializer):
    tag = TagSerializer()

    class Meta:
        model = RecipeTag
        fields = ['tag', 'created_at']


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'amount']


class RecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(many=True, source='ingredients.all')
    image = Base64ImageField()
    tags = serializers.ListField(child=serializers.IntegerField())

    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'tags', 'cooking_time', 'text', 'ingredients', 'author']

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        author = self.context['request'].user
        recipe = Recipe.objects.create(author=author, **validated_data)

        for ingredient_data in ingredients_data:
            ingredient_id = ingredient_data.get('id')
            amount = ingredient_data.get('amount')
            if amount is None:
                raise serializers.ValidationError("Amount is required for each ingredient.")
            ingredient = Ingredient.objects.get(id=ingredient_id)
            RecipeIngredient.objects.create(recipe=recipe, ingredient=ingredient, amount=amount)

        recipe.tags.set(tags_data)
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)
        instance.cooking_time = validated_data.get('cooking_time', instance.cooking_time)
        instance.text = validated_data.get('text', instance.text)
        instance.save()
        instance.ingredients.clear()
        for ingredient_data in ingredients_data:
            ingredient = Ingredient.objects.get(id=ingredient_data.get('ingredient')['id'])
            RecipeIngredient.objects.create(recipe=instance, ingredient=ingredient,
                                            amount=ingredient_data.get('amount'))
        instance.tags.set(tags_data)
        return instance


class SubscriptionSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    author = UserSerializer()

    class Meta:
        model = Subscription
        fields = ['id', 'user', 'author']


class FavoriteSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    recipe = RecipeSerializer()

    class Meta:
        model = Favorite
        fields = ['id', 'user', 'recipe']


class ShoppingListSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    recipe = RecipeSerializer()

    class Meta:
        model = ShoppingList
        fields = ['id', 'user', 'recipe']
