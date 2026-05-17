from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import (
    Utilisateur, ProfilProfessionnel, ExperienceProfessionnelle,
    Competence, MessageContact, Signalement
)

class FormulaireInscriptionCandidat(UserCreationForm):
    """Inscription chercheur d'emploi."""
    first_name = forms.CharField(
        max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    telephone = forms.CharField(
        max_length=20, required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    password1 = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    password2 = forms.CharField(
        label="Confirmer le mot de passe",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Utilisateur
        fields = ['first_name', 'last_name', 'email', 'telephone', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Utilisateur.objects.filter(email=email).exists():
            raise forms.ValidationError("Cet email est déjà utilisé.")
        return email

    def save(self, commit=True):
        utilisateur = super().save(commit=False)
        utilisateur.est_candidat = True
        utilisateur.username = self.cleaned_data['email'].split('@')[0]
        if commit:
            utilisateur.save()
        return utilisateur

class FormulaireInscriptionRecruteur(UserCreationForm):
    """Inscription recruteur."""
    first_name = forms.CharField(
        max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    telephone = forms.CharField(
        max_length=20, required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    password1 = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    password2 = forms.CharField(
        label="Confirmer le mot de passe",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = Utilisateur
        fields = ['first_name', 'last_name', 'email', 'telephone', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Utilisateur.objects.filter(email=email).exists():
            raise forms.ValidationError("Cet email est déjà utilisé.")
        return email

    def save(self, commit=True):
        utilisateur = super().save(commit=False)
        utilisateur.est_recruteur = True
        utilisateur.username = self.cleaned_data['email'].split('@')[0]
        if commit:
            utilisateur.save()
        return utilisateur

class FormulaireProfil(forms.ModelForm):
    """Formulaire d'édition du profil."""
    competences_saisie = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ex: Python, Flutter, JavaScript (séparez par des virgules)'
        }),
        label="Compétences",
        help_text="Saisissez vos compétences séparées par des virgules."
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5})
    )

    class Meta:
        model = ProfilProfessionnel
        fields = ['domaine', 'niveau_etude', 'description', 'photo', 'localisation', 'ouvert_au_travail']
        widgets = {
            'domaine': forms.Select(attrs={'class': 'form-select'}),
            'niveau_etude': forms.Select(attrs={'class': 'form-select'}),
            'localisation': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            competences = ', '.join([c.nom for c in self.instance.competences.all()])
            self.fields['competences_saisie'].initial = competences

class FormulaireExperience(forms.ModelForm):
    """Formulaire d'ajout d'expérience."""
    class Meta:
        model = ExperienceProfessionnelle
        fields = ['poste', 'entreprise', 'date_debut', 'date_fin', 'poste_actuel', 'description']
        widgets = {
            'poste': forms.TextInput(attrs={'class': 'form-control'}),
            'entreprise': forms.TextInput(attrs={'class': 'form-control'}),
            'date_debut': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'date_fin': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'poste_actuel': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

class FormulaireRecherche(forms.Form):
    """Formulaire de recherche de candidats."""
    requete = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Rechercher par compétence...'
        })
    )
    domaine = forms.ChoiceField(
        required=False,
        choices=[('', 'Tous les domaines')] + ProfilProfessionnel._meta.get_field('domaine').choices,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    niveau_etude = forms.ChoiceField(
        required=False,
        choices=[('', 'Tous les niveaux')] + ProfilProfessionnel._meta.get_field('niveau_etude').choices,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

class FormulaireContact(forms.ModelForm):
    """Formulaire de contact recruteur → candidat."""
    class Meta:
        model = MessageContact
        fields = ['sujet', 'message']
        widgets = {
            'sujet': forms.TextInput(attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 6}),
        }
    
class FormulaireSignalement(forms.ModelForm):
    """Formulaire de signalement."""
    class Meta:
        model = Signalement
        fields = ['raison', 'details']
        widgets = {
            'raison': forms.Select(attrs={'class': 'form-select'}),
            'details': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

class FormulaireOTP(forms.Form):
    """Formulaire de vérification OTP."""
    code = forms.CharField(
        max_length=6,
        widget=forms.TextInput(attrs={
            'class': 'form-control text-center',
            'placeholder': '000000',
            'maxlength': '6',
            'style': 'font-size: 2rem; letter-spacing: 0.5rem;'
        }),
        label="Code de vérification"
    )



