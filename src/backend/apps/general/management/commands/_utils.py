from typing import TypeAlias

from django.contrib.auth import get_user_model
from faker import Faker

User = get_user_model()
fake = Faker()


def create_fake_user(password=None) -> TypeAlias:
    """Метод создает и возвращает сгенерированного пользователяю"""
    user = User.objects.create_user(
        email=fake.unique.email(),
        username=fake.unique.user_name(),
        password=password or fake.password(),
    )
    return user
