from django.core.validators import MinValueValidator
from django.db import models
from users.models import User


class Ingredients(models.Model):
    """Модель ингредиентов"""

    name = models.CharField('Продукт', max_length=120)
    measurement_unit = models.CharField(
        'Единица измерения', max_length=120
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name}-{self.measurement_unit}'


class Tags(models.Model):
    """Модель тегов"""

    name = models.CharField('Имя тега', max_length=120, unique=True)
    color = models.CharField(
        'Цвет', max_length=120,
        help_text='RGB', unique=True
    )
    slug = models.SlugField('Адрес', max_length=120, unique=True)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецетов"""

    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='recipes', verbose_name='Автор'
    )
    name = models.CharField('Название', max_length=200)
    tags = models.ManyToManyField(
        Tags, related_name='recipes', verbose_name='Тэг'
    )
    image = models.ImageField('Картинка', upload_to='media/')
    text = models.TextField('Описание')
    cooking_time = models.PositiveSmallIntegerField(
        'Время',
        validators=[MinValueValidator(limit_value=1, message='Не менее 1')]
    )
    ingredients = models.ManyToManyField(
        Ingredients, through='IngredRecipe', related_name='recipes'
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class IngredRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredients, on_delete=models.CASCADE,
        related_name='ingreds', verbose_name='Название ингридиента'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='recipe', verbose_name='Рецепт'
    )
    amount = models.PositiveSmallIntegerField('Количество')

    class Meta:
        verbose_name = 'Ингредиент в рецепт'
        verbose_name_plural = 'Ингредиенты в рецепты'

    def __str__(self):
        return f'{self.ingredient} в {self.recipe}'


class ShoppingCart(models.Model):
    """Список покупок"""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name='Пользователь', related_name='carts'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        verbose_name='Рецепт', related_name='recipes'
    )

    class Meta:
        verbose_name = 'Список покупки'
        verbose_name_plural = 'Список покупок'

    def __str__(self):
        return f'{self.recipe}-->{self.user}'


class Favorite(models.Model):
    """Избранные рецепты"""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name='Пользователь', related_name='favorit'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        verbose_name='Рецепт', related_name='favorits'
    )

    class Meta:
        verbose_name = 'Избраный  рецепт'
        verbose_name_plural = 'Избранные рецепты'

    def __str__(self):
        return f'{self.recipe}-->{self.user}'
