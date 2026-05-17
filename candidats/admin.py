from django.contrib import admin
from .models import (
    Utilisateur, ProfilProfessionnel, Competence,
    ExperienceProfessionnelle, CodeOTP, MessageContact, Signalement
)


@admin.register(Utilisateur)
class AdminUtilisateur(admin.ModelAdmin):
    list_display = [
        'email', 'first_name', 'last_name',
        'est_candidat', 'est_recruteur',
        'email_verifie', 'telephone_verifie', 'badge_verifie', 'est_suspendu'
    ]
    list_filter = ['est_candidat', 'est_recruteur', 'email_verifie', 'est_suspendu']
    search_fields = ['email', 'first_name', 'last_name']
    actions = ['accorder_badge', 'suspendre_comptes', 'reactiver_comptes']

    @admin.action(description="Accorder le badge vérifié")
    def accorder_badge(self, requete, queryset):
        queryset.update(badge_verifie=True)

    @admin.action(description="Suspendre les comptes")
    def suspendre_comptes(self, requete, queryset):
        queryset.update(est_suspendu=True)

    @admin.action(description="Réactiver les comptes")
    def reactiver_comptes(self, requete, queryset):
        queryset.update(est_suspendu=False)


@admin.register(ProfilProfessionnel)
class AdminProfil(admin.ModelAdmin):
    list_display = ['utilisateur', 'domaine', 'niveau_etude', 'localisation', 'ouvert_au_travail']
    list_filter = ['domaine', 'niveau_etude', 'ouvert_au_travail']
    search_fields = ['utilisateur__email', 'utilisateur__first_name', 'utilisateur__last_name']


admin.site.register(Competence)
admin.site.register(ExperienceProfessionnelle)
admin.site.register(CodeOTP)


@admin.register(MessageContact)
class AdminMessage(admin.ModelAdmin):
    list_display = ['recruteur', 'candidat', 'sujet', 'envoye_le', 'lu']
    list_filter = ['lu']


@admin.register(Signalement)
class AdminSignalement(admin.ModelAdmin):
    list_display = ['auteur', 'signale', 'raison', 'cree_le', 'resolu']
    list_filter = ['raison', 'resolu']
    actions = ['resoudre_signalements']

    @admin.action(description="Résoudre les signalements")
    def resoudre_signalements(self, requete, queryset):
        queryset.update(resolu=True)