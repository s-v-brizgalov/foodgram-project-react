from colorfield.fields import ColorField
from django.core.validators import (
    MinValueValidator,
    MaxValueValidator
)
from django.db import models

from users.models import User
from foodgram.settings import MAX_LEN_TITLE, MIN_AMOUNT, MAX_AMOUNT


class Ingredient(models.Model):
    """Класс ингредиент"""

    name = models.CharField(
        verbose_name='Наименование ингредиента',
        max_length=MAX_LEN_TITLE,
        help_text='Наименование ингредиента',
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=MAX_LEN_TITLE,
        help_text='Единица измерения',
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_ingredient_unit'
            )
        ]

    def __str__(self):
        return self.name


class Tag(models.Model):
    """Класс тег"""

    name = models.CharField(
        max_length=50,
        verbose_name='Hазвание',
        unique=True,
        db_index=True
    )

    color = ColorField(
        default='#17A400',
        max_length=7,
        verbose_name='Цвет',
        unique=True,
        help_text='Цвет в формате HEX кода',
    )
    slug = models.SlugField(
        verbose_name='slug',
        unique=True
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name', )

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Класс рецепт"""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='recipes',
        help_text='Автор рецепта',
    )
    name = models.CharField(
        verbose_name='Название рецепта',
        max_length=MAX_LEN_TITLE,
        help_text='Название рецепта',
    )
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='recipes/images',
        help_text='Картинка',
    )
    text = models.TextField(
        verbose_name='Описание',
        help_text='Описание рецепта',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты рецепта',
        through='RecipeIngredient',
        related_name='recipes',
        help_text='Ингредиенты в составе рецепта',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тег рецепта',
        related_name='recipes',
        help_text='Тег рецепта',
    )
    cooking_time = models.IntegerField(
        verbose_name='Время приготовления',
        validators=[
            MinValueValidator(limit_value=MIN_AMOUNT,
                              message=f'min {MIN_AMOUNT}'),
            MaxValueValidator(limit_value=MAX_AMOUNT,
                              message=f'max {MAX_AMOUNT}'),
        ],
        help_text='Время приготовления',
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
        help_text='Дата публикации',
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    """Класс рецепт-интредиент"""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='ingredient',
        help_text='Рецепт',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
        related_name='ingredient',
        help_text='Ингредиент',
    )
    amount = models.IntegerField(
        verbose_name='Количество',
        validators=[
            MinValueValidator(
                limit_value=MIN_AMOUNT,
                message=f'min {MIN_AMOUNT}'),
            MaxValueValidator(
                limit_value=MAX_AMOUNT,
                message=f'max {MAX_AMOUNT}'),
        ],
        help_text='Количество',
    )

    class Meta:
        ordering = ('recipe',)
        verbose_name = 'Количество ингредиента'
        verbose_name_plural = 'Количество ингредиентов'
        constraints = [
            models.UniqueConstraint(
                fields=('recipe', 'ingredient', ),
                name='unique_ingredient',
            ),
        ]

    def __str__(self):
        return f'{self.ingredient} в {self.ingredient.measurement_unit}'


class Follow(models.Model):
    """Класс подписки"""

    follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Подписчик',
        related_name='follower',
        help_text='Подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='author',
        help_text='Автор',
    )

    class Meta:
        ordering = ('author',)
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=('follower', 'author', ),
                name='unique_follow',
            ),
        ]

    def __str__(self):
        return f'{self.follower} подписался на: {self.author}'


class FavoriteRecipe(models.Model):
    """Класс избранное"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='favorite',
        help_text='Пользователь добавивший рецепт',
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Избранное',
        on_delete=models.CASCADE,
        related_name='favorite',
        help_text='Избранный рецепт',
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe', ),
                name='unique_favorite',
            ),
        ]

    def __str__(self):
        return f'{self.recipe} добавлен в избранное'


class ShoppingCart(models.Model):
    """Класс покупок"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='shopping',
        help_text='Пользователь добавивший покупки',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Покупки',
        related_name='shopping',
        help_text='Рецепт для покупок',
    )

    class Meta:
        verbose_name = 'Покупка'
        verbose_name_plural = 'Покупки'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe', ),
                name='unique_shopping',
            ),
        ]

    def __str__(self):
        return f'{self.recipe} добавлен в покупки.'
