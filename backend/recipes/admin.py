from django.contrib import admin

from users.models import User, Subscription

from .models import (Favorite, Ingredient, Recipe, RecipeIngredient, RecipeTag,
                     ShoppingList, Tag)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


class RecipeTagInline(admin.TabularInline):
    model = RecipeTag
    extra = 1


class SubscriptionInline(admin.TabularInline):
    model = Subscription
    fk_name = 'user'
    extra = 1


class FavoriteInline(admin.TabularInline):
    model = Favorite
    fk_name = 'user'
    extra = 1


class ShoppingListInline(admin.TabularInline):
    model = ShoppingList
    fk_name = 'user'
    extra = 1


class RecipeAdmin(admin.ModelAdmin):
    inlines = (RecipeIngredientInline, RecipeTagInline)


class UserAdmin(admin.ModelAdmin):
    inlines = (SubscriptionInline, FavoriteInline, ShoppingListInline)


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient)
admin.site.register(Tag)
admin.site.register(RecipeIngredient)
admin.site.register(Subscription)
admin.site.register(Favorite)
admin.site.register(ShoppingList)
admin.site.register(RecipeTag)

admin.site.register(User, UserAdmin)
