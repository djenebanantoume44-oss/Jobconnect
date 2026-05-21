from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

# Create your models here.
DOMAINES = [
    ('informatique', 'Informatique'),
    ('commerce', 'Commerce'),
    ('sante', 'Santé'),
    ('ingenierie', 'Ingénierie'),
    ('education', 'Éducation'),
    ('finance', 'Finance'),
    ('marketing', 'Marketing'),
    ('rh', 'Ressources Humaines'),
    ('juridique', 'Juridique'),
    ('artisanat', 'Artisanat'),
    ('autre', 'Autre'),
]

NIVEAUX_ETUDE = [
    ('bac', 'Baccalauréat'),
    ('bac+2', 'BAC +2'),
    ('bac+3', 'Licence / BAC +3'),
    ('bac+4', 'Master 1 / BAC +4'),
    ('bac+5', 'Master 2 / BAC +5'),
    ('doctorat', 'Doctorat'),
    ('autre', 'Autre'),
]

RAISONS_SIGNALEMENT = [
    ('faux_profil', 'Faux profil'),
    ('spam', 'Spam / Publicité'),
    ('inapproprie', 'Contenu inapproprié'),
    ('arnaque', 'Tentative d\'arnaque'),
    ('autre', 'Autre'),
]

class  Utilisateur(AbstractUser):
    email = models.EmailField(unique=True, verbose_name="Email")
    telephone = models.CharField(max_length=20, blank=True, verbose_name="Téléphone")
    # Roles(choisit par l'utilisateur) 
    est_candidat = models.BooleanField(default=False, verbose_name="Chercheur d'emploi")
    est_recruteur = models.BooleanField(default=False, verbose_name="Recruteur")

    email_verifie = models.BooleanField(default=False, verbose_name="Email vérifié")
    telephone_verifie = models.BooleanField(default=False, verbose_name="Téléphone vérifié")
    badge_verifie = models.BooleanField(default=False, verbose_name="Profil vérifié")

    #Moderation
    est_suspendu = models.BooleanField(default=False, verbose_name="Suspendu")

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"

def __str__(self):
        return f"{self.get_full_name() or self.username}"

class Competence(models.Model):
       nom = models.CharField(max_length=100, unique=True, verbose_name="compétence")

       class Meta:
              verbose_name = "Compétence"
              verbose_name = "Compétences"
              ordering = ['nom']

       def __str__(self):
               return self.nom
       
class ProfilProfessionnel(models.Model):
       utilisateur = models.OneToOneField(Utilisateur, on_delete=models.CASCADE, related_name='profil')
       domaine = models.CharField(max_length=50, choices=DOMAINES, verbose_name="Domaine")
       niveau_etude = models.CharField(max_length=50, choices=NIVEAUX_ETUDE, verbose_name="Niveau d'etude")
       competences = models.ManyToManyField(Competence, blank=True, verbose_name="Competences")
       description = models.TextField(blank=True, verbose_name="Description personnelle", help_text="Décrivez votre parcours, vos motivations, vos objectifs.")
       photo = models.ImageField(upload_to='photos_profil/', blank=True, null=True, verbose_name="Photode profil")
       localisation = models.CharField(max_length=150, blank=True, verbose_name="Localisation")
       ouvert_au_travail = models.BooleanField(default=True, verbose_name="Ouvert aux opportunités")
       cree_le = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
       mis_a_jour_le = models.DateTimeField(auto_now=True, verbose_name="Mis à jour le")

       class Meta:
              verbose_name = "Profil"
              verbose_name = "Profils"
       def __str__(self):
              return f"Profil de {self.utilisateur}"
       
       @property
       def domaine_affiche(self):
        return dict(DOMAINES).get(self.domaine, self.domaine)

       @property
       def niveau_etude_affiche(self):
        return dict(NIVEAUX_ETUDE).get(self.niveau_etude, self.niveau_etude)
       
class ExperienceProfessionnelle(models.Model):
    profil = models.ForeignKey(
        ProfilProfessionnel, on_delete=models.CASCADE, related_name='experiences'
    )
    poste = models.CharField(max_length=200, verbose_name="Poste")
    entreprise = models.CharField(max_length=200, verbose_name="Entreprise")
    date_debut = models.DateField(verbose_name="Date de début")
    date_fin = models.DateField(blank=True, null=True, verbose_name="Date de fin")
    poste_actuel = models.BooleanField(default=False, verbose_name="Poste actuel")
    description = models.TextField(blank=True, verbose_name="Description")

    class Meta:
        verbose_name = "Expérience"
        verbose_name_plural = "Expériences"
        ordering = ['-date_debut']

    def __str__(self):
        return f"{self.poste} chez {self.entreprise}"

class CodeOTP(models.Model):
    """Code OTP pour vérification email/téléphone."""
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    objet = models.CharField(max_length=10)  # 'email' ou 'telephone'
    cree_le = models.DateTimeField(auto_now_add=True)
    utilise = models.BooleanField(default=False)

    def est_expire(self):
        return (timezone.now() - self.cree_le).total_seconds() > 600

    def __str__(self):
        return f"OTP {self.code} ({self.objet}) - {self.utilisateur}"
    


class MessageContact(models.Model):
    recruteur = models.ForeignKey(
        Utilisateur, on_delete=models.CASCADE, related_name='messages_envoyes'
    )
    candidat = models.ForeignKey(
        Utilisateur, on_delete=models.CASCADE, related_name='messages_recus'
    )
    sujet = models.CharField(max_length=200, verbose_name="Sujet")
    message = models.TextField(verbose_name="Message")
    envoye_le = models.DateTimeField(auto_now_add=True, verbose_name="Envoyé le")
    lu = models.BooleanField(default=False, verbose_name="Lu")

    envoye_par_candidat = models.BooleanField(default=False, verbose_name="Envoyé par le candidat")

    class Meta:
        verbose_name = "Message"
        verbose_name_plural = "Messages"
        ordering = ['-envoye_le']

    def __str__(self):
        return f"De {self.recruteur} à {self.candidat} - {self.sujet}"
    

class Signalement(models.Model):
    auteur = models.ForeignKey(
        Utilisateur, on_delete=models.CASCADE, related_name='signalements_faits'
    )
    signale = models.ForeignKey(
        Utilisateur, on_delete=models.CASCADE, related_name='signalements_recus'
    )
    raison = models.CharField(max_length=20, choices=RAISONS_SIGNALEMENT, verbose_name="Raison")
    details = models.TextField(blank=True, verbose_name="Détails")
    cree_le = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    resolu = models.BooleanField(default=False, verbose_name="Résolu")

    class Meta:
        verbose_name = "Signalement"
        verbose_name_plural = "Signalements"
        unique_together = ['auteur', 'signale']

    def __str__(self):
        return f"Signalement de {self.signale} par {self.auteur}"

       