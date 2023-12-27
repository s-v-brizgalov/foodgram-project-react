from django.conf import settings
from django.contrib import admin

from .models import (FavoriteRecipe, Follow, Ingredient, Recipe,
                     RecipeIngredient, ShoppingCart, Tag)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 0
    min_num = 1


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'measurement_unit')
    list_filter = ('name', )
    list_per_page = settings.PAGE
    search_fields = ('name', )
    empty_value_display = '-пусто-'


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = [RecipeIngredientInline]
    list_display = ('pk', 'name', 'author', 'pub_date', 'text',
                    'get_favorite_count', 'cooking_time', 'image')
    list_filter = ('author__username', 'name', 'tags')
    search_fields = ('author__username', 'name', 'tags__name')
    filter_horizontal = ('tags', )
    empty_value_display = '-пусто-'

    def get_favorite_count(self, obj):
        return obj.favorite.count()

    get_favorite_count.short_description = 'Добавлений в избранное'


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):

    list_display = (
        'pk',
        'recipe',
        'ingredient',
        'amount')
    empty_value_display = '-пусто-'
    list_per_page = settings.PAGE


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'color', 'slug')
    empty_value_display = '-пусто-'
    list_filter = ('name', )
    list_per_page = settings.PAGE
    search_fields = ('name', )
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('pk', 'follower')
    list_filter = ('author', )
    search_fields = ('author__username', 'user__username')

    def following(self, obj):
        return (f'Пользователь {str(obj.user).capitalize()} '
                f'подписан на {str(obj.author).capitalize()}.')

    following.short_description = 'Подписки на пользователей'


@admin.register(FavoriteRecipe)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('pk', 'get_favorite')
    search_fields = ('recipe__name', 'user__username')

    def get_favorite(self, obj):
        return f'"{obj.recipe}" добавлен пользователем {obj.user}.'

    get_favorite.short_description = 'Избранные рецепты'


@admin.register(ShoppingCart)
class ShoppingAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_shopping')
    list_filter = ('recipe', )
    search_fields = ('recipe__name', )
    list_per_page = settings.PAGE

    def get_shopping(self, obj):
        return (f'"{obj.recipe}" добавлен в покупки '
                f'пользователем {str(obj.user).capitalize()}.')

    get_shopping.short_description = 'Рецепты добавленные в покупки.'
