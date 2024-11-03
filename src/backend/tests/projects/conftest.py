import datetime

import pytest

from apps.projects.constants import (
    BUSYNESS_CHOICES,
    MAX_LENGTH_DESCRIPTION,
    MAX_LENGTH_PROJECT_NAME,
    PROJECT_STATUS_CHOICES,
)
from apps.projects.models import Project


@pytest.fixture
def valid_data_project(user):
    return {
        "name": "n" * MAX_LENGTH_PROJECT_NAME,
        "description": "d" * MAX_LENGTH_DESCRIPTION,
        "creator": user,
        "owner": user,
        "started": datetime.date.today(),
        "ended": datetime.date.today() + datetime.timedelta(days=2),
        "busyness": BUSYNESS_CHOICES[0][0],
        "project_status": PROJECT_STATUS_CHOICES[0][0],
    }


@pytest.fixture
def project(valid_data_project):
    return Project.objects.create(**valid_data_project)
