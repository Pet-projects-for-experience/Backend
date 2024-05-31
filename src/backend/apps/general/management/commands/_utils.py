import random
from typing import Sequence, TypeAlias

from django.contrib.auth import get_user_model
from faker import Faker
from faker.providers import T

from apps.general.constants import (
    MAX_LENGTH_SPECIALIZATION_NAME,
    MAX_LENGTH_SPECIALTY_NAME,
)
from apps.general.models import Profession

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


def get_random_professions() -> Sequence[T]:
    """
    Метод возвращает случайное количество Profession.
    Если нужного количество нет, создает новые
    """
    amount_professions = random.randint(1, 5)
    professions_count = Profession.objects.count()
    if professions_count < amount_professions:
        Profession.objects.bulk_create(
            [
                Profession(
                    specialty=fake.text(
                        max_nb_chars=MAX_LENGTH_SPECIALTY_NAME
                    ),
                    specialization=fake.text(
                        max_nb_chars=MAX_LENGTH_SPECIALIZATION_NAME
                    ),
                )
                for _ in range(amount_professions - professions_count)
            ]
        )
    professions = Profession.objects.all()
    return fake.random_choices(professions, amount_professions)
