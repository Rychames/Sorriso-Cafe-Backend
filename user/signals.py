# user/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

User = get_user_model()

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # Aqui você pode adicionar lógica extra quando um usuário é criado
        print(f'Usuário {instance.username} criado com sucesso!')
