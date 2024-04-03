from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.profile.models import Profile
from apps.users.models import User


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile, _ = Profile.objects.get_or_create(user=instance)
    instance.profile.save()
