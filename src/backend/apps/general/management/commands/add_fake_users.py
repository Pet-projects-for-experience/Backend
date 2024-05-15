import csv

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from faker import Faker

from ._utils import create_fake_user

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
                f"{self.amount} users have been added successfully"
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
            user.password = password
            self.users.append(user)
        if self.save:
            self._save_data()

    def _save_data(self):
        """Метод сохраняет данные в файл"""
        with open(self.save, "w") as file:
            writer = csv.writer(file)
            writer.writerow(("id", "email", "username", "password"))
            for user in self.users:
                writer.writerow(
                    (user.id, user.email, user.username, user.password)
                )
