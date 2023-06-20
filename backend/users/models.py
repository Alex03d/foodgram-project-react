from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLES = (
        ('user', 'Аутентифицированный пользователь'),
        ('admin', 'Администратор'),
    )

    DEFAULT_ROLE = ROLES[0][0]

    username = models.CharField(
        'username',
        unique=True, max_length=255
    )

    email = models.EmailField(
        'почта',
        max_length=254,
        blank=False,
        unique=True
    )
    first_name = models.CharField('фамилия', max_length=150, blank=False)

    last_name = models.CharField(('имя'), max_length=150, blank=False)

    password = models.CharField('пароль', max_length=150)

    role = models.CharField(
        'пользовательская роль',
        max_length=33,
        help_text='Администратор или пользователь.'
        'По умолчанию `user`.',
        choices=ROLES,
        default=DEFAULT_ROLE
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('first_name', 'last_name', 'username', )

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ('id', )

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_user(self):
        return self.role == 'user'
