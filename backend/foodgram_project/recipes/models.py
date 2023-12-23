from colorfield.fields import ColorField
from django.core.validators import (MinValueValidator, MaxValueValidator,
                                    RegexValidator)
from django.db import models
from django.db.models import UniqueConstraint

from recipes.constants import (COLOR_LENGTH, DEFAULT_TIME,
                               MAX_TIME, MEASURE_LENGTH,
                               MIN_AMOUNT, MIN_TIME,
                               SLUG_LENGTH, TITLE_LENGTH)
from user.models import User


class Ingredient(models.Model):
    """ Модель ингредиента """
    name = models.CharField(
        max_length=TITLE_LENGTH,
        verbose_name='Название ингредиента'
    )
    measurement_unit = models.CharField(
        max_length=MEASURE_LENGTH,
        verbose_name='Размерность'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)
        constraints = [
            UniqueConstraint(
                fields=('name', 'measurement_unit',),
                name='Этот ингредиент уже есть.'
            )
        ]

    def __str__(self):
        return f'{self.name} ({self.measurement_unit})'


class Tag(models.Model):
    """ Модель тега """
    name = models.CharField(
        max_length=TITLE_LENGTH,
        verbose_name='Название тега',
        unique=True
    )
    color = ColorField(
        verbose_name='Цвет в формате HEX',
        format='hex',
        max_length=COLOR_LENGTH,
        default='#000000',
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^#([A-F0-9]{6})$',
                code='color_error'
            )
        ]
    )
    slug = models.SlugField(
        max_length=SLUG_LENGTH,
        unique=True,
        verbose_name='Уникальный слаг',
        validators=[
            RegexValidator(
                regex=r'^[-a-zA-Z0-9_]+$',
                code='slug_error'
            )
        ]
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """ Модель рецепта """
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор публикации'
    )
    name = models.CharField(
        max_length=TITLE_LENGTH,
        verbose_name='Название',
        blank=False,
        null=False
    )
    image = models.ImageField(
        verbose_name='Изображение',
        blank=False,
        null=False,
        upload_to='static/img/'
    )
    text = models.TextField(
        verbose_name='Описание',
        blank=False,
        null=False
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeComposition',
        through_fields=('recipe', 'ingredient'),
        verbose_name='Ингридиенты'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления - (мин.)',
        blank=False,
        null=False,
        default=DEFAULT_TIME,
        validators=[
            MinValueValidator(
                MIN_TIME,
                message=f'Минимальное время приготовление - '
                        f'{MIN_TIME} мин.'
            ),
            MaxValueValidator(
                MAX_TIME,
                message=f'Максимальное время приготовление - '
                        f'{MAX_TIME} мин.'
            )
        ]
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('name',)

    def __str__(self):
        return self.name


class RecipeComposition(models.Model):
    """" Промежуточная модель для связи ингридиентов с рецептами """
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='ingredient_in_recipe'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
        related_name='ingredient_in_recipe'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        default=MIN_AMOUNT,
        validators=[
            MinValueValidator(
                MIN_AMOUNT,
                message=f'Минимальное количество ингредиента '
                        f'- {MIN_AMOUNT} ед.'
            )
        ]
    )

    class Meta:
        verbose_name = '"Граммовки" рецепта'
        verbose_name_plural = '"Граммовки" рецептов'

    def __str__(self):
        return f'{self.ingredient} - {self.amount}'


class UserRelatRecipe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь избранного рецепта'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Избранный рецепт'
    )

    class Meta:
        abstract = True
        ordering = ('user',)

    def __str__(self):
        return f'{self.user} - {self.recipe}'


class Favorite(UserRelatRecipe):

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        default_related_name = 'favorite'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe',),
                name='unique_user_recipes'
            )
        ]


class ShoppingList(UserRelatRecipe):

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        default_related_name = 'shopping'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe',),
                name='unique_user_recipes_list',
            )
        ]
