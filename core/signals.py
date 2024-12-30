from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, Doctor, Patient, Receptionist

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.role == 'doctor':
            Doctor.objects.create(user=instance)
        elif instance.role == 'patient':
            Patient.objects.create(user=instance)
        elif instance.role == 'receptionist':
            Receptionist.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if instance.role == 'doctor':
        instance.doctor.save()
    elif instance.role == 'patient':
        instance.patient.save()
    elif instance.role == 'receptionist':
        instance.receptionist.save()
