import csv
import random
from typing import TypeAlias

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from faker import Faker

from apps.profile.constants import MAX_LENGTH_ABOUT
from apps.profile.models import Profile

from ._utils import create_fake_user, get_random_professions

User = get_user_model()


class Command(BaseCommand):
    help = "Add fake users"

    def __init__(
        self, stdout=None, stderr=None, no_color=False, force_color=False
    ):
        super().__init__(stdout, stderr, no_color, force_color)
        self.users = list()
        self.fake = Faker()
        self.amount = None
        self.save = None

    def handle(self, *args, **options):
        self.save = options.get("save")
        self.amount = options.get("amount")
        self.add_users()
        self.stdout.write(
            self.style.SUCCESS(
                f"{self.amount} users and "
                f"profiles have been added successfully"
            )
        )
        if self.save:
            self.stdout.write(
                self.style.SUCCESS(
                    f"The data is saved in the file {self.save}"
                )
            )

    def add_arguments(self, parser):
        parser.add_argument(
            "-s",
            "--save",
            action="store",
            default=None,
            help=":str. Save id, email, username and password to "
            "<path_to_file.csv>. Default <None>",
            required=False,
        )
        parser.add_argument(
            "-a",
            "--amount",
            type=int,
            action="store",
            default=1,
            help=":int. Number of users. Default 1",
            required=False,
        )

    def add_users(self):
        for i in range(self.amount):
            password = self.fake.password()
            user = create_fake_user(password=password)
            if not Profile.objects.filter(user=user).exists():
                self.add_profiles(user)
            user.password = password
            self.users.append(user)
        if self.save:
            self._save_data()

    def add_profiles(self, user: TypeAlias):
        for _ in range(self.amount):
            profile = Profile(
                user=user,
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
            profile.professions.add(*get_random_professions())

    def _save_data(self):
        """Метод сохраняет данные в файл"""
        with open(self.save, "w") as file:
            writer = csv.writer(file)
            writer.writerow(("id", "email", "username", "password"))
            for user in self.users:
                writer.writerow(
                    (user.id, user.email, user.username, user.password)
                )
