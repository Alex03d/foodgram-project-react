import base64
import uuid
import webcolors

from rest_framework import serializers
from django.core.files.base import ContentFile
from recipes.models import Recipe, Tag, Ingredient, RecipeIngredient, Subscription, Favorite, ShoppingList
from users.models import User


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            id = uuid.uuid4()
            data = ContentFile(base64.b64decode(imgstr), name=id.urn[9:]+'.'+ext)
        return super().to_internal_value(data)


class Hex2NameColor(serializers.Field):
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        try:
            data = webcolors.hex_to_name(data)
        except ValueError:
            raise serializers.ValidationError('Для этого цвета нет имени')
        return data


class TagSerializer(serializers.ModelSerializer):
    color = Hex2NameColor()

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')
        read_only_fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'measurement_unit']
        read_only_fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount', 'name', 'measurement_unit')

    def __str__(self):
        return f'{self.ingredient} in {self.recipe}'


class RecipeShortSerializer(serializers.ModelSerializer):
    image = serializers.ImageField()

    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'cooking_time']


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes = RecipeShortSerializer(source='recipes_authored', many=True, read_only=True)
    recipes_count = serializers.SerializerMethodField()
    subscriptions_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['email', 'id', 'username', 'first_name', 'last_name', 'is_subscribed', 'recipes', 'recipes_count', 'subscriptions_count']

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user if 'request' in self.context else None
        if user and user.is_authenticated:
            return Subscription.objects.filter(user=user, author=obj).exists()
        return False

    def get_recipes_count(self, obj):
        return obj.recipes_authored.count()

    def get_subscriptions_count(self, obj):
        return Subscription.objects.filter(user=obj).count()


class AuthorSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['email', 'id', 'username', 'first_name', 'last_name', 'is_subscribed']

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user if 'request' in self.context else None
        if user and user.is_authenticated:
            return Subscription.objects.filter(user=user, author=obj).exists()
        return False


class RecipeListSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = AuthorSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(many=True, source='recipeingredients')
    image = Base64ImageField(max_length=None, use_url=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ['id', 'tags', 'author', 'ingredients', 'image',
                  'is_favorited', 'is_in_shopping_cart', 'name',
                  'cooking_time', 'text']

    def get_is_favorited(self, obj):
        user = self.context.get('request').user if 'request' in self.context else None
        if user and user.is_authenticated:
            return Favorite.objects.filter(user=user, recipe=obj).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user if 'request' in self.context else None
        if user and user.is_authenticated:
            return ShoppingList.objects.filter(user=user, recipe=obj).exists()
        return False


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
            RecipeIngredient.objects.create(
                recipe=instance,
                ingredient=Ingredient.objects.get(id=ingredient_data['id']),
                amount=ingredient_data['amount']
            )

        instance.tags.clear()
        for tag in tags_data:
            instance.tags.add(tag.id)

        return instance

    def to_representation(self, instance):
        serializer = RecipeListSerializer(instance, context=self.context)
        return serializer.data


class SubscriptionUserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes = RecipeShortSerializer(source='recipes_authored', many=True, read_only=True)
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['email', 'id', 'username', 'first_name', 'last_name', 'is_subscribed', 'recipes', 'recipes_count']

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user if 'request' in self.context else None
        if user and user.is_authenticated:
            return Subscription.objects.filter(user=user, author=obj).exists()
        return False

    def get_recipes_count(self, obj):
        return obj.recipes_authored.count()


class SubscriptionSerializer(serializers.ModelSerializer):
    author = SubscriptionUserSerializer(read_only=True)

    class Meta:
        model = Subscription
        fields = ['author']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        author_representation = representation.pop('author')
        return {**representation, **author_representation}
