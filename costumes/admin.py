from django.contrib import admin
from .models import Costume, TypeCostume, Acteur, HistoriqueEmprunt, Representation, Essayage
from django.utils import timezone


@admin.register(TypeCostume)
class TypeCostumeAdmin(admin.ModelAdmin):
    list_display = ['libelle', 'epoque']
    search_fields = ['libelle', 'epoque']


@admin.register(Acteur)
class ActeurAdmin(admin.ModelAdmin):
    list_display = ['nom', 'prenom', 'mensurations', 'user']
    search_fields = ['nom', 'prenom']


@admin.register(Costume)
class CostumeAdmin(admin.ModelAdmin):
    list_display = ['type_costume', 'couleur', 'taille', 'etat', 'acteur', 'date_emprunt']
    list_filter = ['etat', 'couleur', 'taille', 'type_costume']
    search_fields = ['type_costume__libelle', 'description']
    readonly_fields = ['date_ajout']
    actions = ['reinitialiser_emprunts']

    def reinitialiser_emprunts(self, request, queryset):
        count = 0
        for costume in queryset.filter(acteur__isnull=False):
            HistoriqueEmprunt.objects.create(
                costume=costume, acteur=costume.acteur, action='reset',
                date_action=timezone.now().date(),
                note='Réinitialisation via interface admin',
                enregistre_par=request.user
            )
            costume.acteur = None
            costume.date_emprunt = None
            costume.save()
            count += 1
        self.message_user(request, f'{count} emprunt(s) réinitialisé(s).')
    reinitialiser_emprunts.short_description = "Réinitialiser les dates d'emprunt"


@admin.register(HistoriqueEmprunt)
class HistoriqueEmpruntAdmin(admin.ModelAdmin):
    list_display = ['costume', 'acteur', 'action', 'date_action', 'enregistre_par']
    list_filter = ['action', 'date_action']
    search_fields = ['costume__type_costume__libelle', 'acteur__nom']
    readonly_fields = ['enregistre_par']


@admin.register(Representation)
class RepresentationAdmin(admin.ModelAdmin):
    list_display = ['titre', 'date_debut', 'date_fin', 'lieu', 'statut', 'nb_essayages']
    list_filter = ['statut']
    search_fields = ['titre', 'lieu']

    def nb_essayages(self, obj):
        return obj.nb_essayages
    nb_essayages.short_description = "Essayages"


@admin.register(Essayage)
class EssayageAdmin(admin.ModelAdmin):
    list_display = ['representation', 'acteur', 'costume', 'date_essayage', 'heure', 'statut']
    list_filter = ['statut', 'representation']
    search_fields = ['acteur__nom', 'representation__titre']
    readonly_fields = ['enregistre_par', 'date_creation']
