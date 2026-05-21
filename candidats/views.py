import random
from unittest import result
from urllib import request
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Q
from django.core.mail import send_mail
from django.conf import settings

from .models import (
    Utilisateur, ProfilProfessionnel, Competence,
    ExperienceProfessionnelle, CodeOTP, MessageContact, Signalement
)
from .forms import (
    FormulaireInscriptionCandidat, FormulaireInscriptionRecruteur,
    FormulaireProfil, FormulaireExperience, FormulaireRecherche,
    FormulaireContact, FormulaireSignalement, FormulaireOTP
)

def accueil(request):
    """Page d'accueil publique."""
    nombre_candidats = Utilisateur.objects.filter(
        est_candidat=True, est_suspendu=False, profil__isnull=False
    ).count()
    nombre_recruteurs = Utilisateur.objects.filter(
        est_recruteur=True, est_suspendu=False
    ).count()
    return render(request, 'candidats/accueil.html', {
        'nombre_candidats': nombre_candidats,
        'nombre_recruteurs': nombre_recruteurs,
    })

def inscription_candidat(request):
    if request.user.is_authenticated:
        return redirect('tableau_de_bord')
    if request.method == 'POST':
        formulaire = FormulaireInscriptionCandidat(request.POST)
        if formulaire.is_valid():
            utilisateur = formulaire.save()
            _generer_et_envoyer_otp(utilisateur, 'email')
            messages.success(request, "Compte créé ! Vérifiez votre email pour le code de confirmation.")
            return redirect('verifier_otp', utilisateur_id=utilisateur.id, objet='email')
    else:
        formulaire = FormulaireInscriptionCandidat()
    return render(request, 'candidats/inscription_candidat.html', {'formulaire': formulaire})

def inscription_recruteur(request):
    if request.user.is_authenticated:
        return redirect('tableau_de_bord')
    if request.method == 'POST':
        formulaire = FormulaireInscriptionRecruteur(request.POST)
        if formulaire.is_valid():
            utilisateur = formulaire.save()
            _generer_et_envoyer_otp(utilisateur, 'email')
            messages.success(request, "Compte créé ! Vérifiez votre email pour le code de confirmation.")
            return redirect('verifier_otp', utilisateur_id=utilisateur.id, objet='email')
    else:
        formulaire = FormulaireInscriptionRecruteur()
    return render(request, 'candidats/inscription_recruteur.html', {'formulaire': formulaire})

def verifier_otp(request, utilisateur_id, objet):
    """Vérifie le code OTP envoyé par email."""
    utilisateur = get_object_or_404(Utilisateur, id=utilisateur_id)

    otp_obj = CodeOTP.objects.filter(
        utilisateur=utilisateur, objet=objet, utilise=False
    ).last()
    code_dev = otp_obj.code if (otp_obj and settings.DEBUG) else None

    if request.method == 'POST':
        formulaire = FormulaireOTP(request.POST)
        if formulaire.is_valid():
            code = formulaire.cleaned_data['code']
            if otp_obj and not otp_obj.est_expire() and code == otp_obj.code:
                otp_obj.utilise = True
                otp_obj.save()
                if objet == 'email':
                    utilisateur.email_verifie = True
                    utilisateur.save()
                    login(request, utilisateur, backend='django.contrib.auth.backends.ModelBackend')
                    messages.success(request, "Email vérifié avec succès !")
                elif objet == 'telephone':
                    utilisateur.telephone_verifie = True
                    utilisateur.save()
                    messages.success(request, "Téléphone vérifié avec succès !")
                return redirect('tableau_de_bord')
            else:
                messages.error(request, "Code invalide ou expiré. Réessayez.")
    else:
        formulaire = FormulaireOTP()

    return render(request, 'candidats/verifier_otp.html', {
        'formulaire': formulaire,
        'utilisateur': utilisateur,
        'objet': objet,
        'code_dev': code_dev,
    })

def _generer_et_envoyer_otp(utilisateur, objet):
    """Génère un code OTP à 6 chiffres et l'envoie par email."""
    code = f"{random.randint(0, 999999):06d}"
    CodeOTP.objects.create(utilisateur=utilisateur, code=code, objet=objet)

    if objet == 'email':
        sujet = "JobConnect - Code de vérification"
        message = f"Bonjour {utilisateur.first_name},\n\nVotre code de vérification est : {code}\n\nCe code expire dans 10 minutes."
        send_mail(sujet, message, settings.EMAIL_HOST_USER, [utilisateur.email], fail_silently=False)

def renvoyer_otp(request, utilisateur_id, objet):
    """Renvoie un nouveau code OTP."""
    utilisateur = get_object_or_404(Utilisateur, id=utilisateur_id)
    _generer_et_envoyer_otp(utilisateur, objet)
    messages.info(request, "Un nouveau code a été envoyé.")
    return redirect('verifier_otp', utilisateur_id=utilisateur.id, objet=objet)

def connexion(request):
    if request.user.is_authenticated:
        return redirect('tableau_de_bord')
    if request.method == 'POST':
        formulaire = AuthenticationForm(request, data=request.POST) 
        if formulaire.is_valid():
            utilisateur = formulaire.get_user()
            if utilisateur.est_suspendu:
                messages.error(request, "Votre compte a été suspendu. Contactez le support.")
                return redirect('connexion')
            login(request, utilisateur)
            messages.success(request, f"Bienvenue, {utilisateur.first_name} !")
            return redirect('tableau_de_bord')
    else:
        formulaire = AuthenticationForm()
    return render(request, 'candidats/connexion.html', {'formulaire': formulaire})

def deconnexion(request):
    logout(request)
    messages.info(request, "Vous êtes déconnecté.")
    return redirect('accueil')

#  TABLEAU DE BORD
@login_required
def tableau_de_bord(request):
    if request.user.est_candidat:
        return tableau_de_bord_candidat(request)
    elif request.user.est_recruteur:
        return tableau_de_bord_recruteur(request)
    return redirect('accueil')

@login_required
def tableau_de_bord_candidat(request):
    """Tableau de bord du chercheur d'emploi."""
    profil = getattr(request.user, 'profil', None)
    nombre_messages_non_lus = request.user.messages_recus.filter(lu=False).count()
    return render(request, 'candidats/tableau_de_bord_candidat.html', {
        'profil': profil,
        'nombre_messages_non_lus': nombre_messages_non_lus,
    })

@login_required
def tableau_de_bord_recruteur(request):
    """Tableau de bord du recruteur."""
    total_messages = request.user.messages_envoyes.count()
    total_candidats = Utilisateur.objects.filter(
        est_candidat=True, est_suspendu=False, profil__isnull=False
    ).count()
    return render(request, 'candidats/tableau_de_bord_recruteur.html', {
        'total_messages': total_messages,
        'total_candidats': total_candidats,
    })

@login_required
def modifier_profil(request):
    """Édition du profil professionnel."""
    profil, _ = ProfilProfessionnel.objects.get_or_create(utilisateur=request.user)
    if request.method == 'POST':
        formulaire = FormulaireProfil(request.POST, request.FILES, instance=profil)
        if formulaire.is_valid():
            profil_sauvegarde = formulaire.save()
            competences_texte = formulaire.cleaned_data.get('competences_saisie', '')
            if competences_texte:
                noms = [c.strip() for c in competences_texte.split(',') if c.strip()]
                objets = []
                for nom in noms:
                    competence, _ = Competence.objects.get_or_create(
                        nom__iexact=nom, defaults={'nom': nom}
                    )
                    objets.append(competence)
                profil_sauvegarde.competences.set(objets)
            else:
                profil_sauvegarde.competences.clear()
            messages.success(request, "Profil mis à jour avec succès.")
            return redirect('tableau_de_bord')
    else:
        formulaire = FormulaireProfil(instance=profil)
    return render(request, 'candidats/modifier_profil.html', {'formulaire': formulaire})

@login_required
def ajouter_experience(request):
    """Ajout d'une expérience professionnelle."""
    profil = get_object_or_404(ProfilProfessionnel, utilisateur=request.user)
    if request.method == 'POST':
        formulaire = FormulaireExperience(request.POST)
        if formulaire.is_valid():
            experience = formulaire.save(commit=False)
            experience.profil = profil
            experience.save()
            messages.success(request, "Expérience ajoutée.")
            return redirect('tableau_de_bord')
    else:
        formulaire = FormulaireExperience()
    return render(request, 'candidats/ajouter_experience.html', {'formulaire': formulaire})

@login_required
def supprimer_experience(request, experience_id):
    """Suppression d'une expérience."""
    experience = get_object_or_404(
        ExperienceProfessionnelle, id=experience_id, profil__utilisateur=request.user
    )
    experience.delete()
    messages.success(request, "Expérience supprimée.")
    return redirect('tableau_de_bord')

def voir_profil(request, utilisateur_id):
    """Vue publique d'un profil candidat."""
    utilisateur = get_object_or_404(
        Utilisateur, id=utilisateur_id, est_candidat=True, est_suspendu=False
    )
    profil = get_object_or_404(ProfilProfessionnel, utilisateur=utilisateur)
    peut_contacter = (
        request.user.is_authenticated
        and request.user.est_recruteur
        and request.user != utilisateur
    )
    peut_signaler = (
        request.user.is_authenticated
        and request.user != utilisateur
    )
    return render(request, 'candidats/voir_profil.html', {
        'utilisateur_profil': utilisateur,
        'profil': profil,
        'peut_contacter': peut_contacter,
        'peut_signaler': peut_signaler,
    })

@login_required
def rechercher_candidats(request):
    """Recherche de candidats par domaine/compétence."""
    if not request.user.est_recruteur:
        messages.error(request, "Accès réservé aux recruteurs.")
        return redirect('tableau_de_bord')

    resultats = ProfilProfessionnel.objects.filter(
        utilisateur__est_candidat=True,
        utilisateur__est_suspendu=False,
        utilisateur__email_verifie=True
    ).select_related('utilisateur').prefetch_related('competences', 'experiences')

    formulaire = FormulaireRecherche(request.GET or None)
    if formulaire.is_valid():
        requete = formulaire.cleaned_data.get('requete', '')
        domaine = formulaire.cleaned_data.get('domaine', '')
        niveau = formulaire.cleaned_data.get('niveau_etude', '')

        if requete:
            resultats = resultats.filter(
                Q(competences__nom__icontains=requete)
                | Q(description__icontains=requete)
                | Q(experiences__poste__icontains=requete)
                | Q(experiences__entreprise__icontains=requete)
            ).distinct()
        if domaine:
            resultats = resultats.filter(domaine=domaine)
        if niveau:
            resultats = resultats.filter(niveau_etude=niveau)


    resultats = resultats.order_by('-mis_a_jour_le')
    
    # ── PAGINATION (9 candidats par page) ──
    paginateur = Paginator(resultats, 9)
    page = request.GET.get('page')
    
    try:
        resultats = paginateur.page(page)
    except PageNotAnInteger:
        resultats = paginateur.page(1)
    except EmptyPage:
        resultats = paginateur.page(paginateur.num_pages)

    return render(request, 'candidats/rechercher.html', {
        'formulaire': formulaire,
        'resultats': resultats,
    })


@login_required
def contacter_candidat(request, candidat_id):
    """Envoi d'un message à un candidat."""
    if not request.user.est_recruteur:
        messages.error(request, "Accès réservé aux recruteurs.")
        return redirect('tableau_de_bord')

    candidat = get_object_or_404(
        Utilisateur, id=candidat_id, est_candidat=True, est_suspendu=False
    )
    if request.method == 'POST':
        formulaire = FormulaireContact(request.POST)
        if formulaire.is_valid():
            msg = formulaire.save(commit=False)
            msg.recruteur = request.user
            msg.candidat = candidat
            msg.save()
            send_mail(
                f"JobConnect - Nouveau message : {msg.sujet}",
                f"Vous avez reçu un message de {request.user.get_full_name()}.\n\nConnectez-vous pour le lire.",
                settings.EMAIL_HOST_USER,
                [candidat.email],
                fail_silently=True,
            )
            messages.success(request, "Message envoyé avec succès.")
            return redirect('voir_profil', utilisateur_id=candidat.id)
    else:
         formulaire = FormulaireContact()
    return render(request, 'candidats/contacter_candidat.html', {
        'formulaire': formulaire,
        'candidat': candidat,
    })

@login_required
def boite_reception(request):
    """Boîte de réception du candidat."""
    if not request.user.est_candidat:
        messages.error(request, "Accès réservé aux chercheurs d'emploi.")
        return redirect('tableau_de_bord')

    liste_messages = request.user.messages_recus.select_related('recruteur').all()
    
    # ── PAGINATION (8 messages par page) ──
    paginateur = Paginator(liste_messages, 8)
    page = request.GET.get('page')
    
    try:
        liste_messages = paginateur.page(page)
    except PageNotAnInteger:
        liste_messages = paginateur.page(1)
    except EmptyPage:
        liste_messages = paginateur.page(paginateur.num_pages)

    return render(request, 'candidats/boite_reception.html', {
        'liste_messages': liste_messages,
    })

@login_required
def marquer_comme_lu(request, message_id):
    """Marquer un message comme lu."""
    msg = get_object_or_404(MessageContact, id=message_id, candidat=request.user)
    msg.lu = True
    msg.save()
    return redirect('boite_reception')

@login_required
def signaler_profil(request, utilisateur_id):
    """Signaler un profil suspect."""
    utilisateur_signale = get_object_or_404(Utilisateur, id=utilisateur_id)
    if utilisateur_signale == request.user:
        messages.error(request, "Vous ne pouvez pas vous signaler vous-même.")
        return redirect('accueil')
    
    deja_signale = Signalement.objects.filter(
        auteur=request.user,
        signale=utilisateur_signale
    ).exists()

    if deja_signale:
        messages.warning(request, "Vous avez déjà signalé ce compte.")
        return redirect('voir_profil', utilisateur_id=utilisateur_id)

    if request.method == 'POST':
        formulaire = FormulaireSignalement(request.POST)
        if formulaire.is_valid():
            signalement = formulaire.save(commit=False)
            signalement.auteur = request.user
            signalement.signale = utilisateur_signale
            signalement.save()
            messages.success(request, "Signalement envoyé. Merci de votre vigilance.")
            return redirect('voir_profil', utilisateur_id=utilisateur_id)
    else:
        formulaire = FormulaireSignalement()
    return render(request, 'candidats/signaler.html', {
        'formulaire': formulaire,
        'utilisateur_signale': utilisateur_signale,

    })

@login_required
def verifier_telephone(request):
    """Demande et vérification OTP par téléphone (envoyé par email en dev)."""
    if request.method == 'POST':
        _generer_et_envoyer_otp(request.user, 'telephone')
        messages.info(request, "Code de vérification envoyé (par email en mode développement).")
        return redirect('verifier_otp', utilisateur_id=request.user.id, objet='telephone')
    return redirect('tableau_de_bord')


def test_email(request):
    send_mail(
        'Test',
        'Email test',
        settings.EMAIL_HOST_USER,
        ['tonemail@gmail.com'],
        fail_silently=False,
    )

    return HttpResponse("Email envoyé")



