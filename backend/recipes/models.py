from django.contrib.auth import get_user_model
from django.db import models


class Tag(models.Model):
    title = models.CharField(max_length=50, unique=True)
    color = models.CharField(max_length=7, unique=True)
    slug = models.SlugField(max_length=50, unique=True)


class Ingredient(models.Model):
    name = models.CharField(max_length=200)
    measurement_unit = models.CharField(max_length=50)


class Recipe(models.Model):
    author = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='recipes'
    )
    name = models.CharField(max_length=200)
    image = models.ImageField(upload_to='recipes/')
    description = models.TextField()
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientAmount',
        through_fields=('recipe', 'ingredient'),
    )
    tags = models.ManyToManyField(Tag, related_name='recipes')
    cooking_time = models.PositiveIntegerField()
    pub_date = models.DateTimeField(auto_now_add=True)


class IngredientAmount(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField()


class FavoriteRecipe(models.Model):
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='favorite_recipes'
    )
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)


class ShoppingList(models.Model):
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='shopping_lists'
    )
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)


class Follow(models.Model):
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='follower'
    )
    author = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='following'
    )
