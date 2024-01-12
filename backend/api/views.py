from django.http import FileResponse
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from djoser import views
from rest_framework import status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import action
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly
)
from rest_framework.response import Response

from recipes.models import (Ingredient, FavoriteRecipe, Follow,
                            Recipe, RecipeIngredient, ShoppingCart, Tag)
from users.models import User

from .filters import IngredientSearchFilter, RecipeFilter
from .pagination import CustomPagination
from .permissions import IsAuthorOrAdminOrReadOnly
from .serializers import (CustomUserSerializer, IngredientSerializer,
                          FollowSerializer, FollowShowSerializer,
                          GetTokenSerializer,
                          RecipeCreateSerializer, RecipeListSerializer,
                          ShortRecipeSerializer, TagSerializer)
from .utils import post, forming_pdf


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
    permission_classes = [IsAuthenticatedOrReadOnly]


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Список тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = [IsAuthenticatedOrReadOnly]


class RecipeViewSet(viewsets.ModelViewSet):
    """Рецепты."""
    queryset = Recipe.objects.all()
    pagination_class = CustomPagination
    permission_classes = (IsAuthorOrAdminOrReadOnly,)
    filterset_class = RecipeFilter
    filter_backends = (DjangoFilterBackend,)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeListSerializer
        return RecipeCreateSerializer

    def update(self, request, *args, **kwargs):  # лишний метод
        """Обновление рецепта."""
        instance = self.get_object()
        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=True
        )
        if 'ingredients' not in request.data:
            return Response(
                {'ingredients': ['This field is required.']},
                status=status.HTTP_400_BAD_REQUEST
            )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

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
            if not (Recipe.objects.filter(id=pk).first()):
                return Response(status=status.HTTP_400_BAD_REQUEST)
            return post(
                request, pk, Recipe,
                FavoriteRecipe, ShortRecipeSerializer
            )
        get_object_or_404(Recipe, id=pk)
        user_id = request.user.id
        delete_cnt, _ = FavoriteRecipe.objects.filter(
            user__id=user_id,
            recipe__id=pk
        ).delete()
        if not delete_cnt:
            return Response(
                {'subcribe': 'Нет избранного.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk=None):
        if request.method == 'POST':
            if not (Recipe.objects.filter(id=pk).first()):
                return Response(status=status.HTTP_400_BAD_REQUEST)
            return post(
                request, pk, Recipe,
                ShoppingCart, ShortRecipeSerializer
            )
        get_object_or_404(ShoppingCart, recipe_id=pk)
        delete_cnt, _ = ShoppingCart.objects.filter(
            user__id=request.user.id,
            recipe__id=pk
        ).delete()
        if not delete_cnt:
            return Response(
                {'subcribe': 'Нет покупок.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

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
