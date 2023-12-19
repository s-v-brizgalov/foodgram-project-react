from django.contrib.auth.password_validation import validate_password
from django.core import exceptions
from django.core.validators import RegexValidator
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from product.models import (Favorite, Ingredients, IngredRecipe, Recipe,
                            ShoppingCart, Tags, User)
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from users.models import Subscriptions


class UserSerializer(UserSerializer):
    """Сериализатор списка пользователей"""

    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = [
            'email', 'id', 'username',
            'first_name', 'last_name', 'is_subscribed'
        ]

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if not user.is_anonymous:
            return Subscriptions.objects.filter(
                user=user, author=obj.id
            ).exists()
        return False


class UserCreateSerializer(UserCreateSerializer):
    """Создание нового пользователя"""
    email = serializers.EmailField(
        validators=[
            UniqueValidator(queryset=User.objects.all()),
            RegexValidator(
                r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
                'Invalid email format')
        ]
    )
    username = serializers.CharField(
        validators=[
            RegexValidator(
                r"^[a-zA-Z0-9]+$",
                'Invalid username format')
        ]
    )

    class Meta:
        model = User
        fields = ['email', 'username', 'first_name', 'last_name', 'password']


class SetPassword(serializers.Serializer):
    """Сериализатор изменение пароля"""
    new_password = serializers.CharField()
    current_password = serializers.CharField()

    def validate(self, obj):
        try:
            validate_password(obj['new_password'])
        except exceptions.ValidationError:
            raise serializers.ValidationError()
        return super().validate(obj)

    def update(self, instance, validated_data):
        if not instance.check_password(validated_data['current_password']):
            raise serializers.ValidationError(
                {'current_password': 'Пароли должны совпадать'}
            )
        if (validated_data['current_password']
                == validated_data['new_password']):
            raise serializers.ValidationError(
                {'new_password': 'Новый пароль должен отличаться от текущего.'}
            )

        instance.set_password(validated_data['new_password'])
        instance.save()
        return validated_data


class IngredientsSerializer(serializers.ModelSerializer):
    """Сериализатор ингридиентов"""

    class Meta:
        model = Ingredients
        fields = ['id', 'name', 'measurement_unit']


class IngredientsAmoutSerializer(serializers.ModelSerializer):
    """Сериализатор количество ингридиентов"""
    id = serializers.IntegerField()
    amount = serializers.IntegerField(write_only=True)

    class Meta:
        model = IngredRecipe
        fields = ['id', 'amount']


class TagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tags
        fields = ['id', 'name', 'color', 'slug']


class RecipeminSerializer(serializers.ModelSerializer):
    """Сериализатор списка рецетов без ингридиентов"""

    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'cooking_time']


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор списка рецептов"""
    tags = TagsSerializer(many=True, read_only=True)
    ingredients = IngredientsSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = [
            'id', 'tags', 'author', 'ingredients',
            'is_favorited', 'is_in_shopping_cart', 'name',
            'image', 'text', 'cooking_time'
        ]

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if not request:
            return False
        return Favorite.objects.filter(recipe=obj, user=request.user).exists()

    def get_is_in_shopping_cart(self, obj):
        return ShoppingCart.objects.filter(recipe=obj).exists()


class RecipeCreateSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tags.objects.all(), many=True
    )
    author = UserSerializer(read_only=True)
    image = Base64ImageField()
    ingredients = IngredientsAmoutSerializer(many=True)

    class Meta:
        model = Recipe
        fields = [
            'id', 'tags', 'author',
            'ingredients', 'image', 'name',
            'text', 'cooking_time'
        ]

    def validate(self, obj):
        for field in ['name', 'text', 'cooking_time']:
            if not obj.get(field):
                raise serializers.ValidationError(
                    f'{field} - Обязательное поле.'
                )
        if not obj.get('tags'):
            raise serializers.ValidationError(
                'Нужно указать минимум 1 тег.'
            )
        if not obj.get('ingredients'):
            raise serializers.ValidationError(
                'Нужно указать минимум 1 ингредиент.'
            )
        inrgedient_id_list = [item['id'] for item in obj.get('ingredients')]
        unique_ingredient_id_list = set(inrgedient_id_list)
        if len(inrgedient_id_list) != len(unique_ingredient_id_list):
            raise serializers.ValidationError(
                'Ингредиенты должны быть уникальны.'
            )
        return obj

    def create(self, validated_data):
        author = self.context.get('request').user
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.tags.set(tags)
        for ingredient in ingredients:
            amount = ingredient['amount']
            ingredient = get_object_or_404(Ingredients, pk=ingredient['id'])
            IngredRecipe.objects.create(
                ingredient=ingredient,
                recipe=recipe,
                amount=amount
            )

        return recipe

    def update(self, instance, validated_data):
        recipe = instance
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time',
            instance.cooking_time
        )
        instance.tags.clear()
        tags = validated_data.get('tags')
        instance.tags.set(tags)
        IngredRecipe.objects.filter(recipe=recipe).all().delete()
        ingredients = validated_data.get('ingredients')
        self.create_ingredients(recipe, ingredients)
        instance.save()
        return instance


class SubscriptionsSerializer(serializers.ModelSerializer):
    """Сериализатор подписки на автора"""
    is_subscribed = serializers.SerializerMethodField()
    recipes = RecipeminSerializer(many=True)
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'email', 'id', 'username',
            'first_name', 'last_name', 'is_subscribed',
            'recipes', 'recipes_count'
        ]

    def get_is_subscribed(self, obj):
        user = get_object_or_404(User, username=obj.username)
        author = get_object_or_404(User, username=obj.username)
        return Subscriptions.objects.filter(
            user=user,
            author=author
        ).exists()

    def get_recipes_count(self, obj):
        return obj.recipes.count()
