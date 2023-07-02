import base64
import uuid

import webcolors
from django.core.files.base import ContentFile
from django.core.exceptions import ValidationError
from django.db import transaction
from rest_framework import serializers, status


from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingList, Tag, RecipeTag)
from users.models import User, Subscription


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            id = uuid.uuid4()
            data = ContentFile(
                base64.b64decode(imgstr),
                name=id.urn[9:] + '.' + ext
            )

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
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')

    def __str__(self):
        return f'{self.ingredient} in {self.recipe}'


class RecipeShortSerializer(serializers.ModelSerializer):
    image = serializers.ImageField()

    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'cooking_time']


class MyUserCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'email',
            'username',
            'first_name',
            'last_name',
            'password',
        )

    def validate_email(self, value):
        lower_email = value.lower()
        if User.objects.filter(email__iexact=lower_email).exists():
            raise ValidationError(
                'Пользователь с таким email уже зарегистрирован'
            )
        return lower_email

    def validate_username(self, value):
        lower_username = value.lower()
        if User.objects.filter(username__iexact=lower_username).exists():
            raise ValidationError(
                'Пользователь с таким username уже зарегистрирован'
            )
        if value == "me":
            raise ValidationError(
                'Невозможно создать пользователя с таким именем!'
            )
        return lower_username

    def create(self, validated_data):
        print('начинаю создавать новый пользователь в MyUserCreate')
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        user.save()
        user.set_password(validated_data['password'])
        print('создан новый пользователь в MyUserCreate')
        return user


class MyUserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes = RecipeShortSerializer(
        source='recipes_authored',
        many=True,
        read_only=True
    )
    recipes_count = serializers.SerializerMethodField()
    subscriptions_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'recipes',
                  'recipes_count', 'subscriptions_count', 'password']

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        user = request.user if request else None
        if user and user.is_authenticated:
            return Subscription.objects.filter(user=user, author=obj).exists()
        return False

    def get_recipes_count(self, obj):
        return obj.recipes_authored.count()

    def get_subscriptions_count(self, obj):
        return Subscription.objects.filter(user=obj).count()

    def create(self, validated_data):
        print('начинаю создавать новый пользователь в MyUser')
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        if 'password' in validated_data:
            user.set_password(validated_data['password'])
        user.save()
        print('создан новый пользователь в MyUser')
        return user


class AuthorSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed']

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        user = request.user if request else None
        if user and user.is_authenticated:
            return Subscription.objects.filter(user=user, author=obj).exists()
        return False


class RecipeListSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = AuthorSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        many=True,
        source='recipeingredients'
    )
    image = Base64ImageField(max_length=None, use_url=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ['id', 'tags', 'author', 'ingredients', 'image',
                  'is_favorited', 'is_in_shopping_cart', 'name',
                  'cooking_time', 'text']

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        user = request.user if request else None
        if user and user.is_authenticated:
            return Favorite.objects.filter(user=user, recipe=obj).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        user = request.user if request else None
        if user and user.is_authenticated:
            return ShoppingList.objects.filter(user=user, recipe=obj).exists()
        return False


class RecipeSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    author = MyUserSerializer(read_only=True)
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
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

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

        request = self.context.get('request')
        user = (
            request.user
            if request and request.user.is_authenticated
            else None
        )

        if not user or not user.is_authenticated:
            raise serializers.ValidationError("Authentication is  required.")

        if not user or not user.is_authenticated:
            raise serializers.ValidationError("Authentication is  required.")

        recipe = Recipe.objects.create(author=user, **validated_data)

        recipe.tags.add(*tags_data)

        ingredients_to_create = []
        for ingredient_data in ingredients_data:
            ingredients_to_create.append(RecipeIngredient(
                recipe=recipe,
                ingredient=Ingredient.objects.get(id=ingredient_data['id']),
                amount=ingredient_data['amount']
            ))

        RecipeIngredient.objects.bulk_create(ingredients_to_create)

        recipe.save()
        return recipe

    def to_representation(self, instance):
        context = {'request': self.context.get('request')}
        return RecipeListSerializer(instance, context=context).data


class AuthorWithoutRecipesSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed']

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        user = request.user if request else None
        if user and user.is_authenticated:
            return Subscription.objects.filter(user=user, author=obj).exists()
        return False


class RecipeUpdateSerializer(serializers.ModelSerializer):
    tags = serializers.SerializerMethodField()
    author = AuthorWithoutRecipesSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        many=True,
        source='recipeingredients')
    image = Base64ImageField(required=False, allow_null=True, use_url=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def to_internal_value(self, data):
        tag_ids = data.get('tags', [])
        data['tags'] = [Tag.objects.get(id=id) for id in tag_ids]
        return super().to_internal_value(data)

    def update(self, instance, validated_data):
        with transaction.atomic():
            tags_data = (
                validated_data.pop('tags', None)
                if 'tags' in validated_data
                else None
            )
            ingredients_data = (
                validated_data.pop('recipeingredients', None)
                if 'recipeingredients' in validated_data
                else None
            )

            for attr, value in validated_data.items():
                setattr(instance, attr, value)

            instance.save()

            if ingredients_data is not None:
                for ingredient in instance.recipeingredients.all():
                    if (
                            ingredient.ingredient.id not in
                            [i['id'] for i in ingredients_data]
                    ):
                        ingredient.delete()

                for ingredient_data in ingredients_data:
                    RecipeIngredient.objects.update_or_create(
                        recipe=instance,
                        ingredient=Ingredient.objects.get(
                            id=ingredient_data['id']
                        ),
                        defaults={'amount': ingredient_data['amount']}
                    )


            if tags_data is not None:
                instance.tags.clear()
                for tag in tags_data:
                    instance.tags.add(tag)
        print('завершаю обновление')
        return instance

    def get_tags(self, obj):
        tags = Tag.objects.filter(recipe=obj)
        return TagSerializer(tags, many=True).data

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        user = request.user if request else None
        if user and user.is_authenticated:
            return Favorite.objects.filter(user=user, recipe=obj).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        user = request.user if request else None
        if user and user.is_authenticated:
            return ShoppingList.objects.filter(user=user, recipe=obj).exists()
        return False


class SubscriptionUserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes = RecipeShortSerializer(
        source='recipes_authored',
        many=True,
        read_only=True
    )
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count']

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        user = request.user if request else None
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
