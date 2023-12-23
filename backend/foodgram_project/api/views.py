from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404, HttpResponse
from django.db.models import Sum
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.permissions import (AllowAny, IsAuthenticated)
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
from rest_framework.views import status

from api.filters import RecipeFilter, IngredientFilter
from api.permissions import IsAuthorOrAuthenticatedOrReadOnly
from api.serializers import (UserSerializer, UserCreateSerializer,
                             IngredientSerializer, TagSerializer,
                             RecipeSerializer, FavoriteSerializer,
                             SubscriberListSerializer,
                             RecipeCreateSerializer, ShoppingListSerializer)

from recipes.models import (Recipe, Ingredient, RecipeComposition,
                            Tag, Favorite, ShoppingList)
from user.models import User, Subscriber


class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = None

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return UserSerializer
        return UserCreateSerializer

    @action(detail=True, methods=['get'],
            permission_classes=(IsAuthenticated,),
            pagination_class=None)
    def me(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data,
                        status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, pk):
        signer = get_object_or_404(User, id=pk)
        serializer = SubscriberListSerializer(signer, data=request.data,
                                              context={"request": request})
        serializer.is_valid(raise_exception=True)
        Subscriber.objects.create(subscriber=request.user, signer=signer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def subscribe_delete(self, request, pk):
        signer = get_object_or_404(User, id=pk)
        get_object_or_404(Subscriber,
                          subscriber=request.user,
                          signer=signer).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    pagination_class = None
    filterset_class = IngredientFilter
    filter_backends = [DjangoFilterBackend]


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = PageNumberPagination
    permission_classes = (IsAuthorOrAuthenticatedOrReadOnly,)
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_queryset(self):
        recipes = Recipe.objects.prefetch_related(
            'ingredient_in_recipe__ingredient', 'tags'
        ).all()
        return recipes

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeSerializer
        return RecipeCreateSerializer

    @action(
        detail=True,
        methods=['post'],
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        if not Favorite.objects.filter(user=request.user,
                                       recipe=recipe).exists():
            new_favorite = Favorite.objects.create(user=request.user,
                                                   recipe=recipe)
            serializer = FavoriteSerializer(new_favorite, data=request.data,
                                            context={"request": request})
            serializer.is_valid(raise_exception=True)
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)

    @favorite.mapping.delete
    def favorite_delete(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        get_object_or_404(Favorite, user=request.user,
                          recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk):
        user = request.user
        data = {'user': user.id,
                'recipe': pk}
        serializer = ShoppingListSerializer(data=data,
                                            context={"request": request}
                                            )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @shopping_cart.mapping.delete
    def shopping_list_delete(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        get_object_or_404(ShoppingList,
                          user=user,
                          recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        ingredients = RecipeComposition.objects.filter(
            recipe__shopping__user=request.user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(ingredient_amount=Sum('amount'))
        shopping_list = ['Список покупок:\n']
        for ingredient in ingredients:
            name = ingredient['ingredient__name']
            measurement_unit = ingredient['ingredient__measurement_unit']
            amount = ingredient['ingredient_amount']
            shopping_list.append(f'\n{name} - {amount} {measurement_unit}')
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = ('attachment;'
                                           'filename="shopping_list.txt"')
        return response


class UserFollowViewSet(viewsets.ModelViewSet):
    serializer_class = SubscriberListSerializer

    def get_queryset(self):
        return User.objects.filter(signers__subscriber=self.request.user)
