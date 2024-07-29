import pytest
from django.contrib.auth import get_user_model

from apps.profile.models import Profile

User = get_user_model()


@pytest.mark.django_db
def test_create_profile_with_user():
    """Тест автоматического создания профиля при создании пользователя"""
    assert Profile.objects.count() == 0
    User.objects.create_user(
        email="test@test.com",
        username="test",
        password="Pa$$W0RD",
    )
    assert Profile.objects.count() == 1


@pytest.mark.django_db
def test_update_profiles_data(profile, update_data):
    """Тест обновления информации в профиле"""
    assert Profile.objects.filter(**update_data).count() == 0
    for field, value in update_data.items():
        setattr(profile, field, value)
    profile.save()
    assert Profile.objects.filter(**update_data).count() == 1
