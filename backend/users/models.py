from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class User(AbstractUser):
    """Модель пользователя"""

    email = models.EmailField(
        verbose_name='Электронная почта',
        max_length=254,
        unique=True,
        db_index=True,
    )

    username = models.CharField(
        verbose_name='Логин',
        max_length=150,
        unique=True,
        db_index=True,
        validators=[RegexValidator(
            regex=r'^(?i)(?!.*\bme\b)[\w.@+-]+$',
            message='Использованы запрещенные символы '
            'или особо запрещенное имя *me*'
        )]
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=150,
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=150,
    )
    password = models.CharField(
        verbose_name='Пароль',
        max_length=254,
    )
    is_subscribed = models.BooleanField(
        default=False,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = 'username', 'first_name', 'last_name'

    class Meta:
        ordering = ['id']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.email
