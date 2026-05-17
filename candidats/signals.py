from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Utilisateur, ProfilProfessionnel


@receiver(post_save, sender=Utilisateur)
def creer_profil_candidat(sender, instance, created, **kwargs):
    """Crée automatiquement un profil vide pour chaque chercheur d'emploi."""
    if created and instance.est_candidat:
        ProfilProfessionnel.objects.get_or_create(utilisateur=instance)

        