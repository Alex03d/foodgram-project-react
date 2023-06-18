import base64
from rest_framework import serializers
from recipes.models import Recipe, Ingredient, IngredientAmount, Tag, Follow, FavoriteRecipe, ShoppingList
from drf_extra_fields.fields import Base64ImageField

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.files.base import ContentFile
from django.db import transaction
from django.core.exceptions import ValidationError

User = get_user_model()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'color', 'slug']

    def to_internal_value(self, data):
        tag, created = Tag.objects.get_or_create(pk=data)
        return tag


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'measurement_unit']


class IngredientAmountSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(source='ingredient.measurement_unit')

    class Meta:
        model = IngredientAmount
        fields = ['id', 'name', 'measurement_unit', 'amount']


class IngredientAmountUpdateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientAmount
        fields = ['id', 'amount']


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = ['email', 'id', 'username', 'first_name', 'last_name', 'is_subscribed']

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None:
            return False
        return Follow.objects.filter(user=request.user, author=obj).exists()


class RecipeSerializer(serializers.ModelSerializer):
    tags = serializers.ListField(child=serializers.IntegerField(), required=False)
    author = UserSerializer()
    ingredients = IngredientAmountSerializer(source='ingredientamount_set', many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = Recipe
        fields = ['id', 'tags', 'author', 'ingredients', 'is_favorited', 'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time']

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request is None:
            return False
        return FavoriteRecipe.objects.filter(user=request.user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request is None:
            return False
        return ShoppingList.objects.filter(user=request.user, recipe=obj).exists()

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')

        recipe = Recipe.objects.create(**validated_data)

        tags = Tag.objects.filter(id__in=tags_data)
        recipe.tags.set(tags)

        for ingredient in ingredients_data:
            IngredientAmount.objects.create(recipe=recipe, **ingredient)

        return recipe


class RecipeUpdateSerializer(serializers.ModelSerializer):
    ingredients = IngredientAmountUpdateSerializer(source='ingredientamount_set', many=True)
    tags = serializers.ListField(child=serializers.IntegerField(), required=False)

    class Meta:
        model = Recipe
        fields = ['ingredients', 'tags', 'image', 'name', 'text', 'cooking_time']

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredientamount_set', None)
        tags_data = validated_data.pop('tags')
        validated_data['author_id'] = self.context['request'].user.id

        with transaction.atomic():
            recipe = Recipe.objects.create(**validated_data)

            # Create tags if they don't exist
            for tag_id in tags_data:
                tag, created = Tag.objects.get_or_create(id=tag_id)
                recipe.tags.add(tag)

            if ingredients_data is not None:
                for ingredient in ingredients_data:
                    if 'ingredient_id' not in ingredient:
                        raise ValidationError('Missing ingredient_id in ingredient data.')
                    IngredientAmount.objects.create(recipe=recipe, **ingredient)

        return recipe


    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients', [])
        tags_data = validated_data.pop('tags', [])

        instance = super().update(instance, validated_data)

        tags = Tag.objects.filter(id__in=tags_data)
        instance.tags.set(tags)

        IngredientAmount.objects.filter(recipe=instance).delete()

        for ingredient in ingredients_data:
            IngredientAmount.objects.create(recipe=instance, **ingredient)

        base64_image = validated_data.get('image')
        if base64_image:
            format, imgstr = base64_image.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
            instance.image.save('image.' + ext, data, save=False)

        instance.save()

        return instance



class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'password2', 'email')
        extra_kwargs = {
            'username': {'required': True},
            'email': {'required': True}
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})

        return attrs

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email']
        )

        user.set_password(validated_data['password'])
        user.save()

        return user
