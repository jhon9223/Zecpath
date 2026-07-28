from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import User
from profiles.models import CandidateProfile, EmployerProfile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    print("=== Signal Fired ===")
    print("Created:", created)
    print("Username:", instance.username)
    print("Role:", instance.role)

    if created:
        if instance.role == User.CANDIDATE:
            print("Creating Candidate Profile...")
            CandidateProfile.objects.get_or_create(user=instance)

        elif instance.role == User.EMPLOYER:
            print("Creating Employer Profile...")
            EmployerProfile.objects.get_or_create(user=instance)

        else:
            print("Role did not match!")
