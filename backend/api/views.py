from django.db.models import Exists, OuterRef
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from djoser import views
from rest_framework import mixins, status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from recipes.models import (Ingredient, FavoriteRecipe, Follow,
                            Recipe, RecipeIngredient, ShoppingCart, Tag)
from users.models import User

from .filters import IngredientSearchFilter, RecipeFilter
from .pagination import CustomPagination
from .permissions import IsAdminOrReadOnly, IsAuthorOrAdminOrReadOnly
from .serializers import (CustomUserSerializer, IngredientSerializer,
                          FollowSerializer, FollowShowSerializer,
                          GetTokenSerializer,
                          RecipeCreateSerializer, RecipeListSerializer,
                          ShortRecipeSerializer, TagSerializer)
from .utils import post, forming_pdf


class ListViewSet(mixins.CreateModelMixin,
                  mixins.ListModelMixin,
                  mixins.RetrieveModelMixin,
                  viewsets.GenericViewSet):
    permission_classes = (IsAdminOrReadOnly,)


class AuthToken(ObtainAuthToken):
    """Авторизация"""

    serializer_class = GetTokenSerializer
    permission_classes = (AllowAny, )
    pagination_class = None

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({'auth_token': token.key},
                        status=status.HTTP_201_CREATED)


class CustomUserViewSet(views.UserViewSet):

    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = (IsAuthorOrAdminOrReadOnly, )
    pagination_class = CustomPagination

    @action(
        detail=False,
        methods=['get', 'patch'],
        url_path='me',
        url_name='me',
        permission_classes=(IsAuthenticated, )
    )
    def get_me(self, request):
        """Информация о себе"""

        if request.method == 'PATCH':
            serializer = CustomUserSerializer(
                request.user, data=request.data,
                partial=True, context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = CustomUserSerializer(
            request.user, context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=['post', 'delete'],
        url_path='subscribe',
        url_name='subscribe',
        permission_classes=(IsAuthenticated,)
    )
    def get_subscribe(self, request, id):
        """Подписка/отписка от автора"""

        author = get_object_or_404(User, id=id)
        if request.method == 'POST':
            serializer = FollowSerializer(
                data={'follower': request.user.id, 'author': author.id}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            author_serializer = FollowShowSerializer(
                author, context={'request': request}
            )
            return Response(
                author_serializer.data, status=status.HTTP_201_CREATED
            )
        subscription = get_object_or_404(
            Follow, follower=request.user, author=author
        )
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        url_path='subscriptions',
        url_name='subscriptions',
        permission_classes=(IsAuthenticated, )
    )
    def get_subscriptions(self, request):
        """Список пользователей, на которых есть подписка."""

        authors = User.objects.filter(author__follower=request.user)
        paginator = CustomPagination()
        result_pages = paginator.paginate_queryset(
            queryset=authors, request=request
        )
        serializer = FollowShowSerializer(
            result_pages, context={'request': request}, many=True
        )
        return paginator.get_paginated_response(serializer.data)


class IngredientViewSet(ListViewSet):
    '''Список ингредиентов'''

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (IngredientSearchFilter, )
    search_fields = ('^name', )
    pagination_class = None


class TagViewSet(ListViewSet):
    '''Список тегов.'''

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    '''Рецепты'''

    pagination_class = CustomPagination
    permission_classes = (IsAuthorOrAdminOrReadOnly | IsAdminOrReadOnly,)

    def get_queryset(self):
        queryset = Recipe.objects.select_related(
            'author').prefetch_related('tags')
        favorited = self.request.query_params.get('is_favorited')
        shopping_cart = self.request.query_params.get('is_in_shopping_cart')
        author = self.request.query_params.get('author')
        tags = self.request.query_params.getlist('tags')
        recipe_filter = RecipeFilter(self.request.GET, queryset=queryset)
        queryset = recipe_filter.qs
        if favorited:
            queryset = queryset.filter(favorite__user=self.request.user)
        if shopping_cart:
            queryset = queryset.filter(shopping__user=self.request.user)
        if author:
            queryset = queryset.filter(author=author)
        if tags:
            queryset = queryset.filter(tags__slug__in=tags).distinct()
        if self.request.user.is_authenticated:
            return queryset.annotate(
                favorit=Exists(
                    queryset.filter(
                        favorite__user=self.request.user,
                        favorite__recipe=OuterRef('id'),
                    )
                ),
                shoppings=Exists(
                    queryset.filter(
                        shopping__user=self.request.user,
                        shopping__recipe=OuterRef('id'),
                    )
                ),
            )
        return queryset

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeListSerializer
        return RecipeCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @staticmethod
    def delete(request, pk, get_object, models):
        obj = get_object_or_404(get_object, id=pk)
        if not models.objects.filter(recipe=obj, user=request.user).exists():
            return Response({'message':
                             f'Нет добавленных рецептов{obj}.'})
        models.objects.filter(
            recipe=obj, user=request.user
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk=None):
        if request.method == 'POST':
            return post(
                request, pk, Recipe,
                FavoriteRecipe, ShortRecipeSerializer
            )
        if request.method == 'DELETE':
            return RecipeViewSet.delete(request, pk, Recipe, FavoriteRecipe)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk=None):
        if request.method == 'POST':
            return post(
                request, pk, Recipe,
                ShoppingCart, ShortRecipeSerializer
            )
        if request.method == 'DELETE':
            return RecipeViewSet.delete(request, pk, Recipe, ShoppingCart)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        ingredients = RecipeIngredient.objects.filter(
            recipe__shopping__user=request.user
        ).values_list(
            'ingredient__name', 'ingredient__measurement_unit', 'amount'
        )
        return FileResponse(
            forming_pdf(ingredients),
            as_attachment=True,
            filename='shopping_cart.pdf', )
