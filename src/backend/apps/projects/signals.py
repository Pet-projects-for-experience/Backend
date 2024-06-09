from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.projects.models import InvitationToProject, Project

from .tasks import send_invitation_email


@receiver(post_save, sender=Project)
def create_user_profile(sender, instance, created, **kwargs):
    """Метод присвоения статуса is_organizer пользователю."""

    if created and not instance.creator.is_organizer:
        instance.creator.is_organizer = True
        instance.creator.save()


@receiver(post_save, sender=InvitationToProject)
def send_invite_to_user(sender, instance, created, **kwargs):
    """Метод отправки письма пользователю, когда его приглашают в проект"""
    email = instance.user.email
    if created:
        send_invitation_email.delay(email)
