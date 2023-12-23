from django.contrib import admin

from .models import (Recipe, Tag, Ingredient,
                     RecipeComposition, Favorite,
                     ShoppingList)


class IngredientInRecipeInline(admin.TabularInline):
    model = Recipe.ingredients.through
    extra = 1


class ShoppingListAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'recipe'
    )
    list_filter = ('user', 'recipe')
    search_fields = ('user', 'recipe')


class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'recipe'
    )
    list_filter = ('user', 'recipe')
    search_fields = ('user', 'recipe')


class AmountIngredientAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'recipe',
        'ingredient',
        'amount'
    )
    search_fields = ('recipe',)
    list_filter = ('recipe',)
    list_display_links = ('recipe',)
    empty_value_display = 'Не задано'


class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'measurement_unit'
    )
    search_fields = ('name',)
    list_filter = ('name',)
    list_display_links = ('name',)
    empty_value_display = 'Не задано'


class TagAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'color',
        'slug'
    )
    search_fields = ('name',)
    list_filter = ('name',)
    list_display_links = ('name',)
    empty_value_display = 'Не задано'


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'author',
        'name',
        'image',
        'text',
        'cooking_time'
    )
    search_fields = (
        'author',
        'name'
    )
    list_filter = (
        'author',
        'name',
        'tags'
    )
    list_display_links = ('name',)
    filter_horizontal = (
        'tags',
        'ingredients',
    )
    empty_value_display = 'Не задано'
    inlines = [IngredientInRecipeInline,]


admin.site.register(ShoppingList, ShoppingListAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(RecipeComposition, AmountIngredientAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Recipe, RecipeAdmin)
