from django.contrib import admin
from product.models import (Favorite, Ingredients, IngredRecipe, Recipe,
                            ShoppingCart, Tags)
from users.models import User


class TagsAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')
    prepopulated_fields = {"slug": ("name",)}


class IngredientsAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)


class IngredientsInline(admin.TabularInline):
    model = IngredRecipe
    min_num = 1


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'author', 'favorite_count')
    list_filter = ('name', 'author', 'tags',)
    autocomplete_fields = ('ingredients',)
    search_fields = ('ingredients',)
    inlines = [
        IngredientsInline,
    ]

    def favorite_count(self, obj):
        return obj.favorits.count()


class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name')


admin.site.register(Ingredients, IngredientsAdmin)
admin.site.register(Tags, TagsAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(IngredRecipe)
admin.site.register(ShoppingCart)
admin.site.register(Favorite)
admin.site.register(User, UserAdmin)
