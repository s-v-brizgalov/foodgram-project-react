from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser import views
from recipes.models import (
    FavoriteRecipe, Follow,
    Ingredient, Recipe,
    RecipeIngredient,
    ShoppingCart, Tag
)
from rest_framework import status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import action
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from api.filters import IngredientSearchFilter, RecipeFilter
from api.pagination import CustomPagination
from api.permissions import IsAuthorOrAdminOrReadOnly
from api.serializers import (
    CustomUserSerializer, FavoriteCreateDeleteSerializer,
    FollowSerializer, FollowShowSerializer,
    GetTokenSerializer, IngredientSerializer,
    RecipeCreateSerializer, RecipeListSerializer,
    ShoppingCartCreateDeleteSerializer, TagSerializer)
from api.utils import forming_pdf
from users.models import User


class BaseRelationsViewSet:

    def relation_create(self, request, serializer_class, pk):
        data = {'user': request.user.id, 'recipe': pk}
        serializer = serializer_class(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def relation_delete(self, request, model, pk):
        get_object_or_404(Recipe, id=pk)
        user_id = request.user.id
        deletedata, _ = model.objects.filter(
            user__id=user_id,
            recipe__id=pk
        ).delete()
        if not deletedata:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)


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
                        status=status.HTTP_200_OK)


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
        """Подписка/отписка от автора."""

        author = get_object_or_404(User, id=id)
        if request.method == 'POST':
            serializer = FollowSerializer(
                data={'follower': request.user.id, 'author': author.id},
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        subscription = Follow.objects.filter(
            follower=request.user, author=author
        )
        if subscription:
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'error': 'Вы не подписаны на этого пользователя.'},
            status=status.HTTP_400_BAD_REQUEST
        )

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


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Список ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (IngredientSearchFilter, )
    search_fields = ('^name', )
    pagination_class = None


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Список тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class RecipeViewSet(BaseRelationsViewSet, viewsets.ModelViewSet):
    """Рецепты."""

    queryset = Recipe.objects.all()
    pagination_class = CustomPagination
    permission_classes = (
        IsAuthenticatedOrReadOnly,
        IsAuthorOrAdminOrReadOnly
    )
    filterset_class = RecipeFilter
    filter_backends = (DjangoFilterBackend,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeListSerializer
        return RecipeCreateSerializer

    @action(methods=['post'], detail=True,
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):

        return self.relation_create(
            request,
            FavoriteCreateDeleteSerializer,
            pk
        )

    @favorite.mapping.delete
    def delete_favorite(self, request, pk=None):
        return self.relation_delete(
            request,
            FavoriteRecipe,
            pk
        )

    @action(methods=['post'], detail=True,
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        return self.relation_create(
            request,
            ShoppingCartCreateDeleteSerializer,
            pk
        )

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk=None):
        return self.relation_delete(
            request,
            ShoppingCart,
            pk
        )

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
