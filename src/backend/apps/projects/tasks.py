from django.utils import timezone

from apps.projects.models import Project
from config.celery import app


@app.task
def auto_completion_projects_task():
    Project.objects.filter(
        ended__lt=timezone.localdate(),
        status=Project.ACTIVE,
    ).update(status=Project.ENDED)
