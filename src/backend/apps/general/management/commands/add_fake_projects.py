import random
from typing import Sequence, TypeAlias

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from faker import Faker
from faker.providers import T

from apps.projects.constants import (
    BUSYNESS_CHOICES,
    MAX_LENGTH_DESCRIPTION,
    MAX_LENGTH_DIRECTION_NAME,
    MAX_LENGTH_PROJECT_NAME,
    PROJECT_STATUS_CHOICES,
)
from apps.projects.models import Direction, Project

from ._utils import create_fake_user

User = get_user_model()


class Command(BaseCommand):
    help = "Add fake projects"

    def __init__(
        self, stdout=None, stderr=None, no_color=False, force_color=False
    ):
        super().__init__(stdout, stderr, no_color, force_color)
        self.fake = Faker()
        self.amount = None

    def handle(self, *args, **options):
        self.amount = options.get("amount")
        self.add_projects()
        self.stdout.write(
            self.style.SUCCESS(
                f"{self.amount} projects have been added successfully"
            )
        )

    def add_arguments(self, parser):
        parser.add_argument(
            "-a",
            "--amount",
            type=int,
            action="store",
            default=1,
            help=":int. Number of projects. Default 1",
            required=False,
        )

    def add_projects(self):
        for _ in range(self.amount):
            project = Project(
                name=self.fake.text(max_nb_chars=MAX_LENGTH_PROJECT_NAME),
                description=self.fake.text(
                    max_nb_chars=MAX_LENGTH_DESCRIPTION
                ),
                creator=self._get_or_create_users_without_projects(),
                owner=self._get_or_create_users_without_projects(),
                started=self.fake.date_this_year(),
                ended=self.fake.date_this_year(after_today=True),
                busyness=self.fake.random_element(BUSYNESS_CHOICES)[0],
                status=self.fake.random_element(PROJECT_STATUS_CHOICES)[0],
                link=self.fake.url(),
                phone_number=self.fake.phone_number(),
                telegram_nick=self.fake.name(),
                email=self.fake.email(),
            )
            project.save()
            project.directions.add(*self._get_random_number_directions())
            project.participants.add(
                *self._get_or_create_random_number_users()
            )
            project.favorited_by.add(
                *self._get_or_create_random_number_users()
            )

    def _get_or_create_users_without_projects(self) -> TypeAlias:
        """
        Метод возвращает user который не связан с Проектом,
        если такого не создает нового пользователя.
        """
        user = User.objects.filter(
            created_projects__isnull=True,
            owned_projects__isnull=True,
        ).first()
        if not user:
            user = create_fake_user()
        return user

    def _get_random_number_directions(self) -> Sequence[T]:
        """Метод возвращает случайное количество направлений разработки"""
        random_number = random.randint(1, 5)
        directions_len = Direction.objects.count()
        if directions_len < random_number:
            Direction.objects.bulk_create(
                [
                    Direction(
                        name=self.fake.text(
                            max_nb_chars=MAX_LENGTH_DIRECTION_NAME
                        )
                    )
                    for _ in range(random_number - directions_len)
                ]
            )
        directions = Direction.objects.all()
        return self.fake.random_choices(directions, random_number)

    def _get_or_create_random_number_users(self) -> Sequence[T]:
        random_number = random.randint(1, 10)
        users_len = User.objects.count()
        if users_len < random_number:
            for _ in range(random_number - users_len):
                create_fake_user()
        users = User.objects.all()
        return self.fake.random_choices(users, random_number)
