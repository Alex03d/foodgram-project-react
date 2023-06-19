from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import (Recipe, Ingredient, Tag,
                     RecipeIngredient, Subscription, Favorite,
                     ShoppingList, RecipeTag)


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

# unregister the old UserAdmin and register the new UserAdmin
User = get_user_model()
admin.site.unregister(User)
admin.site.register(User, UserAdmin)