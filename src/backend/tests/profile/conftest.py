import pytest
from django.contrib.auth import get_user_model

from apps.profile.constants import MIN_LENGTH_ABOUT, MIN_LENGTH_NAME

User = get_user_model()


@pytest.fixture
def user():
    return User.objects.create_user(
        email="test_email@test.com",
        username="test_user",
        password="Pa$$W0RD",
    )


@pytest.fixture
def profile(user):
    return user.profile


@pytest.fixture
def update_data():
    return {
        "name": "n" * MIN_LENGTH_NAME,
        "about": "a" * MIN_LENGTH_ABOUT,
        "portfolio_link": "https://testlink.com",
    }
