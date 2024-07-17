from django.utils import timezone
from templated_mail.mail import BaseEmailMessage

from apps.general.constants import URL_TO_PROFILE
from apps.projects.models import Project
from config.celery import app


@app.task
def auto_completion_projects_task():
    Project.objects.filter(
        ended__lt=timezone.localdate(),
        status=Project.ACTIVE,
    ).update(status=Project.ENDED)


@app.task
def send_invitation_email(email):
    context = {
        "url": URL_TO_PROFILE,
    }
    mail = BaseEmailMessage(
        template_name="email/invitation.html", context=context
    )
    mail.send([email])
