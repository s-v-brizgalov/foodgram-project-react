from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from django.core.validators import ValidationError
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from api.serializer import (IngredientsSerializer, RecipeCreateSerializer,
                            RecipeSerializer, SetPassword,
                            SubscriptionsSerializer, TagsSerializer,
                            UserCreateSerializer, UserSerializer)
from product.models import (Favorite, Ingredients, IngredRecipe, Recipe,
                            ShoppingCart, Tags, User)
from users.models import Subscriptions
from .filters import RecipeFilter
from rest_framework.filters import SearchFilter

from .utilis import add_delete_fun


class UserViewSets(UserViewSet):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return UserSerializer
        return UserCreateSerializer

    @action(
        methods=['Post'], detail=False,
        permission_classes=(IsAuthenticated)
    )
    def set_password(self, request):
        serializer = SetPassword(request.user, data=request.data)
        if serializer.is_valid():
            serializer.save()
        return Response(
            {"detail": "Пароль успешно изменен"},
            status=status.HTTP_204_NO_CONTENT
        )

    @action(
        methods=['POST', 'DELETE'], detail=False,
        url_path=r'(?P<pk>\d+)/subscribe'
    )
    def subscribe(self, request, pk):
        user = get_object_or_404(User, username=request.user)
        author = get_object_or_404(User, pk=pk)
        if request.method == 'POST':
            serializer = SubscriptionsSerializer(author)
            if user != author:
                Subscriptions.objects.create(user=user, author=author)
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED
                )
            raise ValidationError('Нельзя подписаться на самого себя')

        Subscriptions.objects.filter(user=user, author=author).delete()
        return Response({'detail': 'Успешная отписка'},
                        status=status.HTTP_204_NO_CONTENT)


class IngredientSearchFilter(SearchFilter):
    search_param = 'name'


class IngredientsViewSets(viewsets.ModelViewSet):
    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializer
    filter_backends = (IngredientSearchFilter,)
    pagination_class = None
    search_fields = ('^name',)


class SubscriptionsViewSets(viewsets.ReadOnlyModelViewSet):
    serializer_class = SubscriptionsSerializer

    def get_queryset(self):
        user = get_object_or_404(User, username=self.request.user)
        subscribes = Subscriptions.objects.filter(user=user).values('author')
        return User.objects.filter(pk__in=subscribes)


class TagsViewSets(viewsets.ReadOnlyModelViewSet):
    queryset = Tags.objects.all()
    serializer_class = TagsSerializer
    filter_backends = (DjangoFilterBackend,)
    pagination_class = None
    filterset_fields = ('id',)


class RecipeViewSets(viewsets.ModelViewSet):
    queryset = Recipe.objects.select_related(
        'author'
    ).prefetch_related('tags', 'ingredients').all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeSerializer
        return RecipeCreateSerializer

    @action(
        methods=['POST', 'DELETE'], detail=False,
        url_path=r'(?P<pk>\d+)/favorite'
    )
    def favorite(self, request, pk):
        return add_delete_fun(request, pk, Favorite)

    @action(
        methods=['POST', 'DELETE'],
        detail=False, url_path=r'(?P<pk>\d+)/shopping_cart'
    )
    def shopping_cart(self, requests, pk):
        return add_delete_fun(requests, pk, ShoppingCart)

    @action(methods=['GET'], detail=False, url_path='download_shopping_cart')
    def download_shopping_cart(self, requests):
        user = get_object_or_404(User, username=requests.user)
        spopping = ShoppingCart.objects.filter(user=user).values('recipe')
        recipe = Recipe.objects.filter(pk__in=spopping)
        ingredient = IngredRecipe.objects.filter(recipe__in=recipe)
        shop_dict = {}
        for i in ingredient:
            shop_dict[i.ingredient] = i.amount
        shop_list = []
        for key, values in shop_dict.items():
            shop_list.append(f'Ингридиент {key} в колчестве {values} \n')

        filename = 'shopping-list.txt'
        response = HttpResponse(shop_list, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response
