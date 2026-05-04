from django import forms
from .models import Costume, TypeCostume, Acteur, HistoriqueEmprunt, Representation, Essayage


class CostumeForm(forms.ModelForm):
    class Meta:
        model = Costume
        fields = ['type_costume', 'couleur', 'taille', 'etat', 'description']
        widgets = {
            'type_costume': forms.Select(attrs={'class': 'form-select'}),
            'couleur': forms.Select(attrs={'class': 'form-select'}),
            'taille': forms.Select(attrs={'class': 'form-select'}),
            'etat': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3,
                                                  'placeholder': 'Description optionnelle...'}),
        }


class EmpruntForm(forms.Form):
    acteur = forms.ModelChoiceField(
        queryset=Acteur.objects.all(),
        label="Acteur",
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label="-- Sélectionner un acteur --"
    )
    date_emprunt = forms.DateField(
        label="Date d'emprunt",
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
    )
    note = forms.CharField(
        label="Note (optionnel)", required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2})
    )


class FiltreInventaireForm(forms.Form):
    type_costume = forms.ModelChoiceField(
        queryset=TypeCostume.objects.all(), required=False,
        label="Type", empty_label="Tous les types",
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'})
    )
    couleur = forms.ChoiceField(
        choices=[('', 'Toutes couleurs')] + Costume.COULEUR_CHOICES,
        required=False, label="Couleur",
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'})
    )
    taille = forms.ChoiceField(
        choices=[('', 'Toutes tailles')] + Costume.TAILLE_CHOICES,
        required=False, label="Taille",
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'})
    )
    etat = forms.ChoiceField(
        choices=[('', 'Tous états'), ('emprunte', 'Emprunté')] + Costume.ETAT_CHOICES,
        required=False, label="État",
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'})
    )
    date_emprunt_depuis = forms.DateField(
        required=False, label="Emprunté depuis",
        widget=forms.DateInput(attrs={'class': 'form-control form-control-sm', 'type': 'date'})
    )
    # ✅ FIX : filtre date_fin ajouté
    date_emprunt_jusqu_au = forms.DateField(
        required=False, label="Jusqu'au",
        widget=forms.DateInput(attrs={'class': 'form-control form-control-sm', 'type': 'date'})
    )


class FiltreHistoriqueForm(forms.Form):
    date_debut = forms.DateField(
        required=False, label="Du",
        widget=forms.DateInput(attrs={'class': 'form-control form-control-sm', 'type': 'date'})
    )
    date_fin = forms.DateField(
        required=False, label="Au",
        widget=forms.DateInput(attrs={'class': 'form-control form-control-sm', 'type': 'date'})
    )
    action = forms.ChoiceField(
        choices=[('', 'Toutes actions')] + HistoriqueEmprunt.ACTION_CHOICES,
        required=False, label="Action",
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'})
    )
    acteur = forms.ModelChoiceField(
        queryset=Acteur.objects.all(), required=False,
        label="Acteur", empty_label="Tous les acteurs",
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'})
    )


class TypeCostumeForm(forms.ModelForm):
    class Meta:
        model = TypeCostume
        fields = ['libelle', 'epoque']
        widgets = {
            'libelle': forms.TextInput(attrs={'class': 'form-control',
                                              'placeholder': 'ex: Robe, Armure, Chapeau...'}),
            'epoque': forms.TextInput(attrs={'class': 'form-control',
                                             'placeholder': 'ex: Médiéval, Baroque...'}),
        }


class ActeurForm(forms.ModelForm):
    username = forms.CharField(
        label="Nom d'utilisateur (login)", required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ex: marie.dupont'}),
        help_text="Laisser vide pour ne pas créer de compte"
    )
    password = forms.CharField(
        label="Mot de passe", required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Mot de passe...'}),
        help_text="Obligatoire si un nom d'utilisateur est saisi"
    )

    class Meta:
        model = Acteur
        fields = ['nom', 'prenom', 'mensurations']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'prenom': forms.TextInput(attrs={'class': 'form-control'}),
            'mensurations': forms.Textarea(attrs={'class': 'form-control', 'rows': 3,
                                                   'placeholder': 'Tour de poitrine, taille, hanches...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.user:
            self.fields['username'].initial = self.instance.user.username
            self.fields['password'].help_text = "Laisser vide pour garder le mot de passe actuel"

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        # ✅ FIX: vérification correcte — password obligatoire seulement en création
        if username and not password:
            is_creation = not (self.instance and self.instance.pk and self.instance.user)
            if is_creation:
                raise forms.ValidationError(
                    "Un mot de passe est requis si un nom d'utilisateur est saisi.")
        return cleaned_data


# ─── NOUVEAU : Formulaires Représentation & Essayage ─────────────────────────

class RepresentationForm(forms.ModelForm):
    class Meta:
        model = Representation
        fields = ['titre', 'description', 'date_debut', 'date_fin', 'lieu', 'statut']
        widgets = {
            'titre': forms.TextInput(attrs={'class': 'form-control',
                                            'placeholder': 'ex: Le Bourgeois Gentilhomme'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'date_debut': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'date_fin': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'lieu': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ex: Salle principale'}),
            'statut': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        date_debut = cleaned_data.get('date_debut')
        date_fin = cleaned_data.get('date_fin')
        if date_debut and date_fin and date_fin < date_debut:
            raise forms.ValidationError("La date de fin doit être après la date de début.")
        return cleaned_data


class EssayageForm(forms.ModelForm):
    class Meta:
        model = Essayage
        fields = ['representation', 'acteur', 'costume', 'date_essayage', 'heure', 'statut', 'notes']
        widgets = {
            'representation': forms.Select(attrs={'class': 'form-select'}),
            'acteur': forms.Select(attrs={'class': 'form-select'}),
            'costume': forms.Select(attrs={'class': 'form-select'}),
            'date_essayage': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'heure': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'statut': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3,
                                           'placeholder': 'Notes sur les ajustements nécessaires...'}),
        }


class FiltreEssayageForm(forms.Form):
    representation = forms.ModelChoiceField(
        queryset=Representation.objects.all(), required=False,
        label="Représentation", empty_label="Toutes les représentations",
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'})
    )
    acteur = forms.ModelChoiceField(
        queryset=Acteur.objects.all(), required=False,
        label="Acteur", empty_label="Tous les acteurs",
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'})
    )
    statut = forms.ChoiceField(
        choices=[('', 'Tous les statuts')] + Essayage.STATUT_CHOICES,
        required=False, label="Statut",
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'})
    )
    date_debut = forms.DateField(
        required=False, label="Du",
        widget=forms.DateInput(attrs={'class': 'form-control form-control-sm', 'type': 'date'})
    )
    date_fin = forms.DateField(
        required=False, label="Au",
        widget=forms.DateInput(attrs={'class': 'form-control form-control-sm', 'type': 'date'})
    )
