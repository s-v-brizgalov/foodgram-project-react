from django.contrib.auth import authenticate
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.exceptions import NotAuthenticated
from rest_framework.validators import UniqueTogetherValidator
from recipes.models import Ingredient, Follow, Recipe, RecipeIngredient, Tag
from users.models import User


class CustomUserSerializer(UserSerializer):
    '''Сериализатор пользователей.'''

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username',
            'first_name', 'last_name', 'is_subscribed'
        )
    read_only_fields = ("is_subscribed",)

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(follower=user, author=obj).exists()


class CustomUserCreateSerializer(UserCreateSerializer):
    '''Сериализатор новых пользователей.'''

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
    '''Сериализатор тегов.'''

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    '''Сериализатор ингредиентов.'''

    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeIngredientsSerializer(serializers.ModelSerializer):
    '''Сериализатор рецепт-ингредиент.'''

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
    '''Сериализатор рецептов.'''

    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = RecipeIngredientsSerializer(many=True, source='ingredient')
    is_favorited = serializers.BooleanField(
        default=False, read_only=True, source='favorit'
    )
    is_in_shopping_cart = serializers.BooleanField(
        default=False, read_only=True, source='shoppings'
    )

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )


class CreateIngredientSerializer(serializers.ModelSerializer):
    '''Сериализатор ингредиентов, для создания рецепта.'''

    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = Ingredient
        fields = (
            'id', 'amount'
        )


class RecipeCreateSerializer(serializers.ModelSerializer):
    '''Сериализатор создания рецепта.'''

    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField()
    ingredients = CreateIngredientSerializer(many=True)

    class Meta:
        model = Recipe
        fields = '__all__'
    # тесты не пускают, говорят, что слишком сложный запрос

    def validate(self, data):
        x_ingredients = data.get('ingredients')
        x_ids = [item['id'] for item in x_ingredients]
        if not Ingredient.objects.filter(id__in=x_ids).exists():
            raise serializers.ValidationError('Из этого не готовят.')
        tags = self.initial_data.get('tags')
        if not tags:
            raise serializers.ValidationError({
                'tags': 'Тег обязателен для заполнения.'
            })
        tags_set = set()
        for tag in tags:
            if tag in tags_set:
                raise serializers.ValidationError({
                    'tags': f'Тег {tag} уже существует, внесите новый.'
                })
            tags_set.add(tag)
        cooking_time = self.initial_data.get('cooking_time')
        if int(cooking_time) <= 0:
            raise serializers.ValidationError(
                'Время приготовления должно быть больше 0'
            )
        image = self.initial_data.get('image')
        if not image:
            raise serializers.ValidationError(
                'Нужна картинка'
            )

        ingredients = self.initial_data.get('ingredients')
        if not ingredients:
            raise serializers.ValidationError(
                'Поле с ингредиентами не может быть пустым'
            )
        unique_ingredients = []
        for ingredient in ingredients:
            id_ingredient = ingredient['id']
            if int(ingredient['amount']) <= 0:
                raise serializers.ValidationError(
                    f'Некорректное количество для {id_ingredient}'
                )
            if not isinstance(int(ingredient['amount']), int):
                raise serializers.ValidationError(
                    'Количество ингредиентов должно быть целым числом'
                )
            if id_ingredient not in unique_ingredients:
                unique_ingredients.append(id_ingredient)
            else:
                raise serializers.ValidationError(
                    'В рецепте не может быть повторяющихся ингредиентов'
                )
        return data

    def create_ingredients(self, recipe, ingredients):
        ingredients_list = []
        for ingredient in ingredients:
            create_ingredients = RecipeIngredient(
                recipe=recipe,
                ingredient_id=ingredient.get('id'),
                amount=ingredient.get('amount'),
            )
            ingredients_list.append(create_ingredients)
        RecipeIngredient.objects.bulk_create(ingredients_list)

    def create(self, validated_data):
        user = self.context['request'].user
        if user.is_anonymous:
            raise NotAuthenticated('нинада')
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.image = validated_data.get('image', instance.image)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        if 'ingredients' in validated_data:
            instance.ingredients.clear()
            self.create_ingredients(
                instance, validated_data.get('ingredients')
            )
        if 'tags' in validated_data:
            tags = validated_data.get('tags')
            instance.tags.set(tags)
        instance.save()
        return instance

    def to_representation(self, instance):
        return RecipeListSerializer(
            instance,
            context={
                'request': self.context.get('request')
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
        """Запрет подписки на себя"""

        if data['follower'] == data['author']:
            raise serializers.ValidationError(
                'Подписка на cамого себя не имеет смысла'
            )
        return data


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Список рецептов в подписке"""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FollowShowSerializer(serializers.ModelSerializer):
    '''Сериализатор списка подписок.'''

    recipes = serializers.SerializerMethodField(method_name='get_recipes')
    recipes_count = serializers.SerializerMethodField(
        method_name='get_recipes_count'
    )

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email',
                  'is_subscribed', 'recipes', 'recipes_count')

    def get_srs(self):

        return ShortRecipeSerializer

    def get_recipes(self, object):
        request = self.context.get('request')
        author_recipes = object.recipes.all()
        recipes_limit = request.query_params.get('recipes_limit')
        if recipes_limit:
            author_recipes = author_recipes[:int(recipes_limit)]
        return ShortRecipeSerializer(author_recipes, many=True).data

    def get_recipes_count(self, object):
        return object.recipes.count()
