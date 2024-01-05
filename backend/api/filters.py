
import django_filters
from django.contrib.auth import get_user_model
from rest_framework.filters import SearchFilter
from recipes.models import Recipe

User = get_user_model()


class IngredientSearchFilter(SearchFilter):
    '''Фильтр ингредиентов.'''

    search_param = 'name'


class RecipeFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains', label='Название')
    is_favorited = django_filters.BooleanFilter(method='get_is_favorited')
    is_in_shopping_cart = django_filters.BooleanFilter(
        method='get_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart',)
