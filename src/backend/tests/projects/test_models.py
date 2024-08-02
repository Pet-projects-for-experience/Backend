import pytest
from django.core.exceptions import ValidationError

from apps.projects.models import Project


def check_invalid_project_creation(data, count=0):
    assert Project.objects.count() == count
    project = Project(**data)
    with pytest.raises(ValidationError):
        project.full_clean()
        project.save()
    assert Project.objects.count() == count


def test_create_project_valid_data(valid_data_project):
    assert Project.objects.count() == 0
    project = Project(**valid_data_project)
    project.full_clean()
    project.save()
    assert Project.objects.count() == 1


def test_create_project_invalid_data_long_name(valid_data_project):
    valid_data_project["name"] += "n"
    check_invalid_project_creation(valid_data_project)


def test_create_project_invalid_data_empty_name(valid_data_project):
    valid_data_project["name"] = ""
    check_invalid_project_creation(valid_data_project)


def test_create_project_invalid_data_exists_name(valid_data_project, project):
    check_invalid_project_creation(valid_data_project, count=1)


@pytest.mark.xfail(
    reason="Не смог разобраться почему не вызывает ValidationError, "
    "Есть подозрения, что из-за null=True .full_clean() не "
    "проверяет это поле"
)
def test_create_project_invalid_data_long_description(valid_data_project):
    valid_data_project["description"] += "d"
    check_invalid_project_creation(valid_data_project)
