import pytest


@pytest.fixture
def user(django_user_model):
    return django_user_model.objects.create(
        email="test_email@test.com",
        username="test_user",
        password="Pa$$W0RD",
    )


@pytest.fixture
def user_client(user, client):
    client.force_login(user)
    return client


@pytest.fixture
def profile(user):
    profile = user.profile
    profile.name = "profile_name"
    profile.save()
    return profile
