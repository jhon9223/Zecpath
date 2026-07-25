from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import User, CandidateProfile, EmployerProfile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, **kwargs):

    if instance.role == User.CANDIDATE:
        CandidateProfile.objects.get_or_create(user=instance)

    elif instance.role == User.EMPLOYER:
        EmployerProfile.objects.get_or_create(user=instance)
