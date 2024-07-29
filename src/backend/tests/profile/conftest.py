import pytest

from apps.profile.constants import MIN_LENGTH_ABOUT, MIN_LENGTH_NAME


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
