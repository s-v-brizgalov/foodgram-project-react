from django_filters.rest_framework import FilterSet, filters
from product.models import Recipe, Tags


class RecipeFilter(FilterSet):
    """Фильтр для рецептов"""
    tags = filters.ModelMultipleChoiceFilter(
        queryset=Tags.objects.all(),
        field_name='tags__slug',
        to_field_name='slug',
    )
    is_favorited = filters.BooleanFilter(method='get_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')

    def get_is_favorited(self, queryset, name, value):
        """Метод для фильтрации избранных рецептов"""
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(favorits__user=self.request.user)
        return queryset

    def get_is_in_shopping_cart(self, queryset, name, value):
        """Метод для фильтрации рецептов в корзине"""
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(recipes__user=self.request.user)
        return queryset
