import random
from typing import Sequence, TypeAlias

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from faker import Faker
from faker.providers import T

from apps.general.constants import LEVEL_CHOICES
from apps.general.models import Profession, Skill
from apps.projects.constants import (
    BUSYNESS_CHOICES,
    MAX_LENGTH_DESCRIPTION,
    MAX_LENGTH_DIRECTION_NAME,
    MAX_LENGTH_PROJECT_NAME,
    PROJECT_STATUS_CHOICES,
)
from apps.projects.models import Direction, Project, ProjectSpecialist

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
        self.directions = Direction.objects.all()
        self.users = User.objects.all()
        self.profession = Profession.objects.all()
        self.skills = Skill.objects.all()
        assert (
            self.profession.count() > 2 or self.skills.count() > 2
        ), "You need to add fixtures Profession and Skill"

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
            self.create_and_add_project_specialists(project)

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
        directions_count = self.directions.count()
        if directions_count < random_number:
            Direction.objects.bulk_create(
                [
                    Direction(
                        name=self.fake.text(
                            max_nb_chars=MAX_LENGTH_DIRECTION_NAME
                        )
                    )
                    for _ in range(random_number - directions_count)
                ]
            )
            self.directions = Direction.objects.all()
        return self.fake.random_choices(self.directions, random_number)

    def _get_or_create_random_number_users(self) -> Sequence[T]:
        random_number = random.randint(1, 10)
        users_count = self.users.count()
        if users_count < random_number:
            for _ in range(random_number - users_count):
                create_fake_user()
            self.users = User.objects.all()
        return self.fake.random_choices(self.users, random_number)

    def create_and_add_project_specialists(self, project) -> None:
        for _ in range(random.randint(2, 5)):
            random_number = random.randint(1, 3)
            project_specialist = ProjectSpecialist(
                project=project,
                profession=self.fake.random_element(self.profession),
                count=random_number,
                level=self.fake.random_element(LEVEL_CHOICES)[0],
                is_required=self.fake.boolean(),
            )
            project_specialist.save()
            project_specialist.skills.add(
                *self.fake.random_choices(self.skills, random_number)
            )
