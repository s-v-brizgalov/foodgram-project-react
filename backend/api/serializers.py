from django.contrib.auth import authenticate
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from recipes.models import (FavoriteRecipe, Follow, Ingredient, Recipe,
                            RecipeIngredient, ShoppingCart, Tag)
from rest_framework import serializers
from rest_framework.exceptions import ParseError
from rest_framework.validators import UniqueTogetherValidator

from api.constant import MAX_AMOUNT, MIN_AMOUNT
from users.models import User


class CustomUserSerializer(UserSerializer):
    """Сериализатор пользователей."""

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username',
            'first_name', 'last_name'
        )

    def get_is_subscribed(self, obj):
        return (
            self.context['request'].user.is_authenticated
            and obj.author.filter(
                follower=self.context['request'].user
            ).exists()
        )


class CustomUserCreateSerializer(UserCreateSerializer):
    """Сериализатор новых пользователей."""

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'password'
        )


class GetTokenSerializer(serializers.Serializer):
    email = serializers.CharField(
        label='Email',
        write_only=True)
    password = serializers.CharField(
        label='Пароль',
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True)
    token = serializers.CharField(
        label='Токен',
        read_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        if email and password:
            user = authenticate(
                request=self.context.get('request'),
                email=email,
                password=password)
            if not user:
                raise serializers.ValidationError(
                    "Невозможно зайти в систему",
                    code='authorization')
        else:
            msg = 'Укажите почту и пароль'
            raise serializers.ValidationError(
                msg,
                code='authorization')
        attrs['user'] = user
        return attrs


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тегов."""

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов."""

    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeIngredientsSerializer(serializers.ModelSerializer):
    """Сериализатор рецепт-ингредиент."""

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            'id', 'name', 'measurement_unit', 'amount'
        )


class RecipeListSerializer(serializers.ModelSerializer):
    """Сериализатор рецептов."""

    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = RecipeIngredientsSerializer(many=True, source='ingredient')
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        return (request and request.user.is_authenticated
                and obj.favorite.filter(
                    user=request.user
                ).exists())

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        return (request and request.user.is_authenticated
                and obj.shopping.filter(
                    user=request.user
                ).exists())


class CreateIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов, для создания рецепта."""

    id = serializers.IntegerField()
    amount = serializers.IntegerField(
        min_value=MIN_AMOUNT,
        max_value=MAX_AMOUNT,
        error_messages={
            'min_value': f'min {MIN_AMOUNT}.',
            'max_value': f'max {MAX_AMOUNT}.'})

    class Meta:
        model = Ingredient
        fields = ('id', 'amount')

    def validate_id(self, value):
        if not Ingredient.objects.filter(id=value).exists():
            raise ParseError('Фантастический ингредиент.')
        return value


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор создания рецепта."""

    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField()
    ingredients = CreateIngredientSerializer(many=True)
    cooking_time = serializers.IntegerField(
        min_value=MIN_AMOUNT,
        max_value=MAX_AMOUNT,
        error_messages={
            'min_value': f'min {MIN_AMOUNT}',
            'max_value': f'max {MAX_AMOUNT}'})

    class Meta:
        model = Recipe
        fields = '__all__'

    def validate(self, data):
        ingredients = data.get('ingredients')
        if ingredients is None:
            raise ParseError('Ингредиентов нет совсем.')
        tags = data.get('tags')
        if not tags:
            raise serializers.ValidationError({
                'tags': 'Тег обязателен для заполнения.'
            })
        if len(tags) != len(set(tags)):
            raise serializers.ValidationError({
                'tags': 'Тег уже существует, внесите новый.'
            })
        image = data.get('image')
        if not image:
            raise serializers.ValidationError(
                'Нужна картинка.'
            )
        ingredient_id = [item['id'] for item in ingredients]
        if len(ingredient_id) != len(set(ingredient_id)):
            raise serializers.ValidationError(
                'Некорректное количество ингредиентов.'
            )
        return data

    def create_ingredients(self, recipe, ingredients):
        create_ingredients = [
            RecipeIngredient(
                recipe=recipe,
                ingredient_id=ingredient['id'],
                amount=ingredient['amount'],
            )
            for ingredient in ingredients
        ]
        RecipeIngredient.objects.bulk_create(create_ingredients)

    def create(self, validated_data):
        user = self.context['request'].user
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data, author=user)
        recipe.tags.set(tags)
        self.create_ingredients(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        instance.tags.clear()
        instance.tags.set(validated_data.pop('tags'))
        instance.ingredients.clear()
        ingredients = validated_data.pop('ingredients')
        self.create_ingredients(instance, ingredients)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeListSerializer(
            instance,
            context={
                'request': self.context['request']
            }).data


class FollowSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Follow."""

    class Meta:
        model = Follow
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('author', 'follower'),
                message='Подписка на этого автора уже есть'
            )
        ]

    def validate(self, data):
        if data['follower'] == data['author']:
            raise serializers.ValidationError(
                'Подписка на cамого себя не имеет смысла'
            )
        return data


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Список рецептов в подписке."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FollowShowSerializer(serializers.ModelSerializer):
    """Сериализатор списка подписок."""

    recipes = serializers.SerializerMethodField(method_name='get_recipes')
    recipes_count = serializers.SerializerMethodField(
        method_name='get_recipes_count'
    )

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email',
                  'recipes', 'recipes_count')

    def get_recipes(self, object):
        request = self.context.get('request')
        author_recipes = object.recipes.all()
        recipes_limit = request.query_params.get('recipes_limit')
        if recipes_limit and recipes_limit.isdigit():
            author_recipes = author_recipes[:int(recipes_limit)]
        return ShortRecipeSerializer(
            author_recipes,
            many=True,
            context=self.context
        ).data

    def get_recipes_count(self, object):
        return object.recipes.count()


class ShoppingCartCreateDeleteSerializer(serializers.ModelSerializer):
    """Общий сериалайзер для избранного и корзины."""

    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')

    def validate(self, data):
        user_id = data.get('user').id
        recipe_id = data.get('recipe').id
        if self.Meta.model.objects.filter(user=user_id,
                                          recipe=recipe_id).exists():
            raise serializers.ValidationError('Уже добавлен.')
        return data

    def to_representation(self, instance):
        serializer = ShortRecipeSerializer(
            instance.recipe, context=self.context)
        return serializer.data


class FavoriteCreateDeleteSerializer(ShoppingCartCreateDeleteSerializer):
    """Сериализатор для избранного."""

    class Meta(ShoppingCartCreateDeleteSerializer.Meta):
        model = FavoriteRecipe
