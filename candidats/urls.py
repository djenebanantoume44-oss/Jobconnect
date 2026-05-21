from django.urls import path
from . import views

urlpatterns = [
    # Pages publiques
    path('', views.accueil, name='accueil'),
    path('connexion/', views.connexion, name='connexion'),
    path('deconnexion/', views.deconnexion, name='deconnexion'),

    # Inscription
    path('inscription/candidat/', views.inscription_candidat, name='inscription_candidat'),
    path('inscription/recruteur/', views.inscription_recruteur, name='inscription_recruteur'),

    # Vérification OTP
    path('verification/<int:utilisateur_id>/<str:type>/', views.verifier_otp, name='verifier_otp'),
    path('renvoyer-otp/<int:utilisateur_id>/<str:type>/', views.renvoyer_otp, name='renvoyer_otp'),
    path('verifier-telephone/', views.verifier_telephone, name='verifier_telephone'),

    # Tableau de bord
    path('tableau-de-bord/', views.tableau_de_bord, name='tableau_de_bord'),

    # Profil chercheur
    path('profil/modifier/', views.modifier_profil, name='modifier_profil'),
    path('profil/ajouter-experience/', views.ajouter_experience, name='ajouter_experience'),
    path('profil/supprimer-experience/<int:experience_id>/', views.supprimer_experience, name='supprimer_experience'),
    path('profil/<int:utilisateur_id>/', views.voir_profil, name='voir_profil'),

    # Recherche (recruteur)
    path('rechercher/', views.rechercher_candidats, name='rechercher'),

    # Messagerie
    path('contacter/<int:candidat_id>/', views.contacter_candidat, name='contacter_candidat'),
    path('messagerie/', views.boite_reception, name='boite_reception'),
    path('messagerie/<int:message_id>/lu/', views.marquer_comme_lu, name='marquer_comme_lu'),

    # Signalement
    path('signaler/<int:utilisateur_id>/', views.signaler_profil, name='signaler'),

    path('test-email/', views.test_email, name='test_email'),
]