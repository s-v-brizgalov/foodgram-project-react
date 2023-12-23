from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from django.db import transaction

from recipes.models import (Recipe, Ingredient,
                            RecipeComposition, Tag,
                            Favorite, ShoppingList)
from user.models import User, Subscriber
from recipes.constants import (MIN_AMOUNT,
                               MIN_TIME,
                               MAX_TIME)


class UserSerializer(serializers.ModelSerializer):
    """ Сериализатор для пользователя. """
    username = serializers.RegexField(regex=r"^[\w.@+-]+\Z")

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name'
        )

    def validate_name(self, username):
        if username.lower() == "me":
            raise serializers.ValidationError(
                'Использовать имя "me" запрещено.'
            )
        return username


class UserCreateSerializer(serializers.ModelSerializer):
    """ Создание пользователя. """

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'password'
        )
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class RecipeShowForUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
            'author'
        )


class SubscriberListSerializer(serializers.ModelSerializer):
    """ Сериализатор для подписок. """
    is_subscribed = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )

    def validate(self, data):
        if self.context['request'].user == data:
            raise serializers.ValidationError(
                'Нельзя подписываться на самого себя.'
            )
        return data

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return (request.user.is_authenticated
                and Subscriber.objects.filter(
                    subscriber=request.user, signer=obj
                ).exists())

    def get_recipes_count(self, author):
        return Recipe.objects.filter(author=author).count()

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = None
        if request:
            recipes_limit = request.query_params.get('recipes_limit')
        recipes = obj.recipes.all()
        if recipes_limit:
            recipes = obj.recipes.all()[:int(recipes_limit)]
        return RecipeShowForUserSerializer(recipes,
                                           many=True,
                                           context={'request': request}).data


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeCompositionSerializer(serializers.ModelSerializer):
    """ Сериализатор для состава рецетпа. """
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeComposition
        fields = ('id', 'name', 'measurement_unit', 'amount')


class TagSerializer(serializers.ModelSerializer):
    """ Сериализатор для тэгов. """

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class RecipeSerializer(serializers.ModelSerializer):
    """ Сериализатор для просмотра всей информации о рецепте. """
    author = UserSerializer(read_only=True)
    image = Base64ImageField()
    ingredients = serializers.SerializerMethodField()
    tags = TagSerializer(many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'author',
            'name',
            'image',
            'text',
            'ingredients',
            'tags',
            'cooking_time',
            'is_favorited',
            'is_in_shopping_cart',
        )

    def get_ingredients(self, instance):
        return RecipeCompositionSerializer(
            instance.ingredient_in_recipe.all(),
            many=True
        ).data

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        return (request.user.is_authenticated
                and Favorite.objects.filter(
                    user=request.user, recipe=obj
                ).exists())

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        return (request.user.is_authenticated
                and ShoppingList.objects.filter(
                    user=request.user, recipe=obj
                ).exists())


class IngredientPOSTSerializer(serializers.ModelSerializer):
    """ Сериализатор для "граммовок" ингредиента в рецепте. """
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeComposition
        fields = ('id', 'amount')

    def validate_amount(self, amount):
        if int(amount) < MIN_AMOUNT:
            raise serializers.ValidationError(
                f'Минимальное количество ингредиента '
                f'- {MIN_AMOUNT} ед.'
            )
        return amount


class RecipeCreateSerializer(serializers.ModelSerializer):
    """ Сериализатор для создания и обновления рецепта. """
    image = Base64ImageField()
    ingredients = IngredientPOSTSerializer(many=True,
                                           source='ingredient_in_recipe')

    class Meta:
        model = Recipe
        fields = (
            'name',
            'image',
            'text',
            'ingredients',
            'tags',
            'cooking_time'
        )

    def validate_cooking_time(self, cooking_time):
        if int(cooking_time) < MIN_TIME:
            raise serializers.ValidationError(
                f'Минимальное время приготовление - '
                f'{MIN_TIME} мин.'
            )
        if int(cooking_time) > MAX_TIME:
            raise serializers.ValidationError(
                f'Максимальное время приготовление - '
                f'{MAX_TIME} мин.'
            )
        return cooking_time

    @transaction.atomic
    def create(self, validated_data):
        request = self.context.get('request')
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredient_in_recipe')
        recipe = Recipe.objects.create(author=request.user, **validated_data)
        recipe.tags.set(tags)
        RecipeComposition.objects.bulk_create([
            RecipeComposition(
                recipe=recipe,
                ingredient=Ingredient.objects.get(pk=ingredient_data['id']),
                amount=ingredient_data['amount']
            )
            for ingredient_data in ingredients
        ])
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredient_in_recipe')
        tags = validated_data.pop('tags')
        instance.tags.clear()
        instance.tags.set(tags)
        RecipeComposition.objects.filter(recipe=instance).delete()
        super().update(instance, validated_data)
        RecipeComposition.objects.bulk_create([
            RecipeComposition(
                recipe=instance,
                ingredient=Ingredient.objects.get(pk=ingredient['id']),
                amount=ingredient['amount']
            )
            for ingredient in ingredients
        ])
        return instance


class FavoriteSerializer(serializers.ModelSerializer):
    recipe = serializers.PrimaryKeyRelatedField(
        read_only=True
    )
    user = serializers.PrimaryKeyRelatedField(
        read_only=True
    )

    class Meta:
        model = Favorite
        fields = ('recipe', 'user')


class ShoppingListSerializer(serializers.ModelSerializer):
    """ Сериализатор для списка покупок. """

    class Meta:
        model = ShoppingList
        fields = ('id', 'user', 'recipe')
