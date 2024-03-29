from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.projects.models import Project


@receiver(post_save, sender=Project)
def create_user_profile(sender, instance, created, **kwargs):
    """Метод присвоения статуса is_organizer пользователю."""

    if created and not instance.creator.is_organizer:
        instance.creator.is_organizer = True
        instance.creator.save()
