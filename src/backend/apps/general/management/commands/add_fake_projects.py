import random
from typing import TypeAlias

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from faker import Faker

from apps.projects.constants import (
    MAX_LENGTH_DESCRIPTION,
    MAX_LENGTH_DIRECTION_NAME,
    MAX_LENGTH_PROJECT_NAME,
)
from apps.projects.models import Direction, Project

from .utils import create_fake_user

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
                busyness=random.randrange(5, 50, 5),
                status=random.randint(1, 3),
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

    def _get_random_number_directions(self) -> list[Direction]:
        """Метод возвращает случайное количество направлений разработки"""
        random_number = random.randint(1, 5)
        directions = list(Direction.objects.all()[:random_number])
        if len(directions) < random_number:
            created_directions = list()
            for _ in range(random_number - len(directions)):
                direction = Direction(
                    name=self.fake.text(max_nb_chars=MAX_LENGTH_DIRECTION_NAME)
                )
                created_directions.append(direction)
            Direction.objects.bulk_create(created_directions)
            directions += created_directions
        return directions

    def _get_or_create_random_number_users(self) -> list[TypeAlias]:
        random_number = random.randint(1, 10)
        users = list(User.objects.all())
        if len(users) < random_number:
            for _ in range(random_number - len(users)):
                users.append(create_fake_user())
        random.shuffle(users)
        return users[:random_number]
