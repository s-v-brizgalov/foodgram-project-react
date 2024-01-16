from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

from api.constant import MAX_LEN_NAME, MAX_LEN_PASSWORD, MAX_LEN_TITLE


class User(AbstractUser):
    """Модель пользователя"""

    email = models.EmailField(
        verbose_name='Электронная почта',
        max_length=MAX_LEN_TITLE,
        unique=True,
        db_index=True,
    )

    username = models.CharField(
        verbose_name='Логин',
        max_length=MAX_LEN_NAME,
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
        max_length=MAX_LEN_NAME,
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=MAX_LEN_NAME,
    )
    password = models.CharField(
        verbose_name='Пароль',
        max_length=MAX_LEN_PASSWORD,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = 'username', 'first_name', 'last_name'

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.email
