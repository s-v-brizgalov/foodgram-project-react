from django.contrib.auth.models import AbstractUser
from django.db import models

from user.constants import EMAIL_LENGTH, ROLE_LENGTH


class User(AbstractUser):
    USER = 'user'
    ADMIN = 'admin'

    ROLES_CHOICES = (
        (USER, USER),
        (ADMIN, ADMIN)
    )
    email = models.EmailField(
        max_length=EMAIL_LENGTH,
        unique=True,
        blank=False,
        null=False,
        verbose_name='Электронная почта'
    )
    role = models.CharField(
        max_length=ROLE_LENGTH,
        choices=ROLES_CHOICES,
        default=USER,
        blank=True,
        verbose_name='Роль'
    )

    @property
    def is_admin(self):
        return self.role == self.ADMIN

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        constraints = [
            models.UniqueConstraint(
                fields=('username', 'email'),
                name='unique_user'
            )
        ]
        ordering = ('id',)

    def __str__(self) -> str:
        return self.username


class Subscriber(models.Model):
    subscriber = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribers',
        verbose_name='Подписчик'
    )
    signer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='signers',
        verbose_name='Пользователь, на которого подписались'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        unique_together = ('subscriber', 'signer')

    def __str__(self):
        return f'{self.subscriber} подписан на {self.signer}.'
