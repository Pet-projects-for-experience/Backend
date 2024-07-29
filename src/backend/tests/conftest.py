import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture
def user():
    return User.objects.create_user(
        email="test_email@test.com",
        username="test_user",
        password="Pa$$W0RD",
    )
