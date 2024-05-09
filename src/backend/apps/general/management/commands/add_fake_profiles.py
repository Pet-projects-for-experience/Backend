import random
from typing import Sequence, TypeAlias

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from faker import Faker
from faker.providers import T

from apps.general.constants import (
    MAX_LENGTH_SPECIALIZATION_NAME,
    MAX_LENGTH_SPECIALTY_NAME,
)
from apps.general.models import Profession
from apps.profile.constants import MAX_LENGTH_ABOUT
from apps.profile.models import Profile

User = get_user_model()


class Command(BaseCommand):
    help = "Add fake profile"

    def __init__(
        self, stdout=None, stderr=None, no_color=False, force_color=False
    ):
        super().__init__(stdout, stderr, no_color, force_color)
        self.fake = Faker()
        self.amount = None

    def handle(self, *args, **options):
        self.amount = options.get("amount")
        self.add_profiles()
        self.stdout.write(
            self.style.SUCCESS(
                f"{self.amount} profiles have been added successfully"
            )
        )

    def add_arguments(self, parser):
        parser.add_argument(
            "-a",
            "--amount",
            type=int,
            action="store",
            default=1,
            help=":int. Number of profiles. Default 1",
            required=False,
        )

    def add_profiles(self):
        for _ in range(self.amount):
            profile = Profile(
                user=self._get_or_create_user(),
                name=self.fake.first_name(),
                about=self.fake.text(max_nb_chars=MAX_LENGTH_ABOUT),
                portfolio_link=self.fake.url(),
                birthday=self.fake.date_of_birth(
                    minimum_age=18, maximum_age=70
                ),
                country=self.fake.country(),
                city=self.fake.city(),
                ready_to_participate=self.fake.boolean(),
                visible_status=random.randint(1, 3),
                visible_status_contacts=random.randint(1, 3),
                allow_notifications=self.fake.boolean(),
                subscribe_to_projects=self.fake.boolean(),
                phone_number=self.fake.phone_number(),
                telegram_nick=self.fake.name(),
                email=self.fake.email(),
            )
            profile.save()
            profile.professions.add(*self._get_random_professions())

    def _get_random_professions(self) -> Sequence[T]:
        """
        Метод возвращает случайное количество Profession.
        Если нужного количество нет, создает новые
        """
        amount_professions = random.randint(1, 5)
        professions = Profession.objects.all()
        if len(professions) != amount_professions:
            new_professions = list()
            for _ in range(amount_professions - len(professions)):
                profession = Profession(
                    specialty=self.fake.text(
                        max_nb_chars=MAX_LENGTH_SPECIALTY_NAME
                    ),
                    specialization=self.fake.text(
                        max_nb_chars=MAX_LENGTH_SPECIALIZATION_NAME
                    ),
                )
                new_professions.append(profession)
            Profession.objects.bulk_create(new_professions)
            professions = Profession.objects.all()
        return self.fake.random_choices(professions, amount_professions)

    def _get_or_create_user(self) -> TypeAlias[User]:
        """
        Метод возвращает user который не связан с профилем,
        если создает нового пользователя.
        """
        user = User.objects.filter(profile__isnull=True).first()
        if not user:
            user = User.objects.create_user(
                email=self.fake.unique.email(),
                username=self.fake.unique.user_name(),
            )
        return user
