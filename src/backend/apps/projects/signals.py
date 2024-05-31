from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.projects.models import InvitationToProject, Project


@receiver(post_save, sender=Project)
def create_user_profile(sender, instance, created, **kwargs):
    """Метод присвоения статуса is_organizer пользователю."""

    if created and not instance.creator.is_organizer:
        instance.creator.is_organizer = True
        instance.creator.save()


@receiver(post_save, sender=InvitationToProject)
def send_invite_to_user(sender, instance, created, **kwargs):
    """Метод отправки письма пользователю, когда его приглашают в проект"""
    if created:
        send_mail(
            "Вас приглашают в проект",
            f"Вы получили приглашение в проект {instance.project.name}",
            "info@codepet.ru",
            (instance.user.email,),
        )
