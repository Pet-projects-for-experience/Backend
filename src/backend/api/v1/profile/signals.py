from django.db.models.signals import post_delete, post_save, pre_save
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


def delete_image(image):
    if image and hasattr(image, "storage") and hasattr(image, "path"):
        storage, path = image.storage, image.path
        storage.delete(path)


@receiver(post_delete, sender=Profile)
def handle_images_on_delete(sender, instance, **kwargs):
    image_file = instance.avatar
    delete_image(image_file)


@receiver(pre_save, sender=Profile)
def set_instance_cache(sender, instance, **kwargs):
    old_instance = sender.objects.filter(pk=instance.pk).first()
    if old_instance:
        instance.media_cache = {"avatar": old_instance.avatar}


@receiver(post_save, sender=Profile)
def handle_images_on_update(sender, instance, **kwargs):
    if hasattr(instance, "media_cache") and instance.media_cache:
        old_image = instance.media_cache["avatar"]
        new_image = getattr(instance, "avatar", None)
        if old_image != new_image:
            delete_image(old_image)
