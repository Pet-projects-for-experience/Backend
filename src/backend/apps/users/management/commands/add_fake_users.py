import csv

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from faker import Faker

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
            help=":str. Save email, username and password to "
            "<path_to_file.csv>. Default <None>"
            "This file os required fo create fake profiles",
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
            user = dict(
                email=self.fake.unique.email(),
                username=self.fake.unique.user_name(),
                password=self.fake.password(),
            )
            self.users.append(user)
            # bulk_create не работает для User из-за хэширования паролей
            User.objects.create_user(**user)
        if self.save:
            self._save_data()

    def _save_data(self):
        with open(self.save, "w") as file:
            writer = csv.writer(file)
            writer.writerow(("email", "username", "password"))
            for user in self.users:
                writer.writerow((user.values()))
