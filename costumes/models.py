from django.db import models
from django.contrib.auth.models import User


class TypeCostume(models.Model):
    libelle = models.CharField(max_length=100, verbose_name="Libellé")
    epoque = models.CharField(max_length=100, blank=True, verbose_name="Époque / Style")

    class Meta:
        verbose_name = "Type de costume"
        verbose_name_plural = "Types de costumes"
        ordering = ['libelle']

    def __str__(self):
        return f"{self.libelle} ({self.epoque})" if self.epoque else self.libelle


class Acteur(models.Model):
    nom = models.CharField(max_length=100, verbose_name="Nom")
    prenom = models.CharField(max_length=100, verbose_name="Prénom")
    mensurations = models.TextField(blank=True, verbose_name="Mensurations")
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True,
                                verbose_name="Compte utilisateur")

    class Meta:
        verbose_name = "Acteur"
        verbose_name_plural = "Acteurs"
        ordering = ['nom', 'prenom']

    def __str__(self):
        return f"{self.prenom} {self.nom}"

    @property
    def nom_complet(self):
        return f"{self.prenom} {self.nom}"


class Costume(models.Model):
    ETAT_CHOICES = [
        ('neuf', 'Neuf'),
        ('bon', 'Bon état'),
        ('reparer', 'À réparer'),
        ('use', 'Usé'),
    ]

    COULEUR_CHOICES = [
        ('rouge', 'Rouge'), ('bleu', 'Bleu'), ('vert', 'Vert'),
        ('noir', 'Noir'), ('blanc', 'Blanc'), ('or', 'Or'),
        ('violet', 'Violet'), ('bordeaux', 'Bordeaux'), ('rose', 'Rose'),
        ('gris', 'Gris'), ('marron', 'Marron'), ('orange', 'Orange'),
    ]

    TAILLE_CHOICES = [
        ('xs', 'XS'), ('s', 'S'), ('m', 'M'),
        ('l', 'L'), ('xl', 'XL'), ('xxl', 'XXL'),
    ]

    type_costume = models.ForeignKey(TypeCostume, on_delete=models.SET_NULL, null=True,
                                     verbose_name="Type de costume")
    couleur = models.CharField(max_length=20, choices=COULEUR_CHOICES, verbose_name="Couleur")
    taille = models.CharField(max_length=5, choices=TAILLE_CHOICES, default='m', verbose_name="Taille")
    etat = models.CharField(max_length=10, choices=ETAT_CHOICES, default='bon', verbose_name="État")
    description = models.TextField(blank=True, verbose_name="Description")
    acteur = models.ForeignKey(Acteur, on_delete=models.SET_NULL, null=True, blank=True,
                               related_name='costumes_empruntes', verbose_name="Acteur emprunteur")
    date_emprunt = models.DateField(null=True, blank=True, verbose_name="Date d'emprunt")
    date_ajout = models.DateTimeField(auto_now_add=True, verbose_name="Date d'ajout")

    class Meta:
        verbose_name = "Costume"
        verbose_name_plural = "Costumes"
        ordering = ['type_costume__libelle']

    def __str__(self):
        type_label = self.type_costume.libelle if self.type_costume else "Costume"
        return f"{type_label} - {self.get_couleur_display()} - {self.get_taille_display()}"

    @property
    def est_emprunte(self):
        return self.acteur is not None

    @property
    def etat_badge_class(self):
        return {'neuf': 'success', 'bon': 'primary', 'reparer': 'warning', 'use': 'danger'}.get(self.etat, 'secondary')

    @property
    def couleur_hex(self):
        return {
            'rouge': '#dc3545', 'bleu': '#0d6efd', 'vert': '#198754',
            'noir': '#212529', 'blanc': '#f8f9fa', 'or': '#ffc107',
            'violet': '#6f42c1', 'bordeaux': '#6d0d23', 'rose': '#e83e8c',
            'gris': '#6c757d', 'marron': '#795548', 'orange': '#fd7e14',
        }.get(self.couleur, '#6c757d')


class HistoriqueEmprunt(models.Model):
    ACTION_CHOICES = [
        ('emprunt', 'Emprunt'),
        ('retour', 'Retour'),
        ('reset', 'Réinitialisation admin'),
    ]

    costume = models.ForeignKey(Costume, on_delete=models.CASCADE,
                                related_name='historique', verbose_name="Costume")
    acteur = models.ForeignKey(Acteur, on_delete=models.SET_NULL, null=True,
                               verbose_name="Acteur")
    action = models.CharField(max_length=10, choices=ACTION_CHOICES, verbose_name="Action")
    date_action = models.DateField(verbose_name="Date de l'action")
    note = models.TextField(blank=True, verbose_name="Note")
    enregistre_par = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                       verbose_name="Enregistré par")

    class Meta:
        verbose_name = "Historique d'emprunt"
        verbose_name_plural = "Historiques d'emprunts"
        ordering = ['-date_action', '-id']

    def __str__(self):
        return f"{self.get_action_display()} - {self.costume} - {self.date_action}"


# ─── NOUVEAU : Gestion des Représentations & Essayages ────────────────────────

class Representation(models.Model):
    STATUT_CHOICES = [
        ('planifiee', 'Planifiée'),
        ('en_cours', 'En cours'),
        ('terminee', 'Terminée'),
        ('annulee', 'Annulée'),
    ]

    titre = models.CharField(max_length=200, verbose_name="Titre de la pièce")
    description = models.TextField(blank=True, verbose_name="Description")
    date_debut = models.DateField(verbose_name="Date de début")
    date_fin = models.DateField(verbose_name="Date de fin")
    lieu = models.CharField(max_length=200, blank=True, verbose_name="Lieu")
    statut = models.CharField(max_length=15, choices=STATUT_CHOICES,
                              default='planifiee', verbose_name="Statut")
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Représentation"
        verbose_name_plural = "Représentations"
        ordering = ['-date_debut']

    def __str__(self):
        return f"{self.titre} ({self.date_debut})"

    @property
    def statut_badge_class(self):
        return {'planifiee': 'info', 'en_cours': 'success', 'terminee': 'secondary', 'annulee': 'danger'}.get(self.statut, 'secondary')

    @property
    def nb_essayages(self):
        return self.essayages.count()

    @property
    def nb_essayages_confirmes(self):
        return self.essayages.filter(statut='confirme').count()


class Essayage(models.Model):
    STATUT_CHOICES = [
        ('planifie', 'Planifié'),
        ('confirme', 'Confirmé'),
        ('annule', 'Annulé'),
    ]

    representation = models.ForeignKey(Representation, on_delete=models.CASCADE,
                                       related_name='essayages', verbose_name="Représentation")
    acteur = models.ForeignKey(Acteur, on_delete=models.CASCADE,
                               related_name='essayages', verbose_name="Acteur")
    costume = models.ForeignKey(Costume, on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='essayages', verbose_name="Costume essayé")
    date_essayage = models.DateField(verbose_name="Date de l'essayage")
    heure = models.TimeField(null=True, blank=True, verbose_name="Heure")
    statut = models.CharField(max_length=10, choices=STATUT_CHOICES,
                              default='planifie', verbose_name="Statut")
    notes = models.TextField(blank=True, verbose_name="Notes / Ajustements")
    enregistre_par = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                       verbose_name="Enregistré par")
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Essayage"
        verbose_name_plural = "Essayages"
        ordering = ['date_essayage', 'heure']

    def __str__(self):
        return f"Essayage {self.acteur.nom_complet} — {self.representation.titre} ({self.date_essayage})"

    @property
    def statut_badge_class(self):
        return {'planifie': 'warning', 'confirme': 'success', 'annule': 'danger'}.get(self.statut, 'secondary')
