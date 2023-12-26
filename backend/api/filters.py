
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
    author = django_filters.CharFilter(field_name='author__username',
                                       label='Автор')
    tags = django_filters.CharFilter(field_name='tags__slug', label='Тег')

    class Meta:
        model = Recipe
        fields = []
