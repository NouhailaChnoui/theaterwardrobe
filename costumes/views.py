from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from .models import Costume, TypeCostume, Acteur, HistoriqueEmprunt, Representation, Essayage
from .forms import (CostumeForm, EmpruntForm, FiltreInventaireForm,
                    FiltreHistoriqueForm, TypeCostumeForm, ActeurForm,
                    RepresentationForm, EssayageForm, FiltreEssayageForm)
from .utils import is_admin  # ✅ FIX: import centralisé


# ─── Inventaire ──────────────────────────────────────────────────────────────

@login_required
def inventaire(request):
    costumes = Costume.objects.select_related('type_costume', 'acteur').all()
    form = FiltreInventaireForm(request.GET or None)

    if form.is_valid():
        if form.cleaned_data.get('type_costume'):
            costumes = costumes.filter(type_costume=form.cleaned_data['type_costume'])
        if form.cleaned_data.get('couleur'):
            costumes = costumes.filter(couleur=form.cleaned_data['couleur'])
        if form.cleaned_data.get('taille'):
            costumes = costumes.filter(taille=form.cleaned_data['taille'])
        etat_val = form.cleaned_data.get('etat')
        if etat_val == 'emprunte':
            costumes = costumes.filter(acteur__isnull=False)
        elif etat_val:
            costumes = costumes.filter(etat=etat_val)
        if form.cleaned_data.get('date_emprunt_depuis'):
            costumes = costumes.filter(date_emprunt__gte=form.cleaned_data['date_emprunt_depuis'])
        # ✅ FIX: filtre date_fin maintenant appliqué
        if form.cleaned_data.get('date_emprunt_jusqu_au'):
            costumes = costumes.filter(date_emprunt__lte=form.cleaned_data['date_emprunt_jusqu_au'])

    total = Costume.objects.count()
    disponibles = Costume.objects.filter(acteur__isnull=True).count()
    empruntes = Costume.objects.filter(acteur__isnull=False).count()
    a_reparer = Costume.objects.filter(etat='reparer').count()

    context = {
        'costumes': costumes, 'form': form,
        'total': total, 'disponibles': disponibles,
        'empruntes': empruntes, 'a_reparer': a_reparer,
        'is_admin': is_admin(request.user),
    }
    return render(request, 'costumes/inventaire.html', context)


@login_required
@user_passes_test(is_admin)
def costume_ajouter(request):
    if request.method == 'POST':
        form = CostumeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Costume ajouté avec succès.')
            return redirect('inventaire')
    else:
        form = CostumeForm()
    return render(request, 'costumes/costume_form.html', {'form': form, 'titre': 'Ajouter un costume'})


@login_required
@user_passes_test(is_admin)
def costume_modifier(request, pk):
    costume = get_object_or_404(Costume, pk=pk)
    if request.method == 'POST':
        form = CostumeForm(request.POST, instance=costume)
        if form.is_valid():
            form.save()
            messages.success(request, 'Costume modifié avec succès.')
            return redirect('inventaire')
    else:
        form = CostumeForm(instance=costume)
    return render(request, 'costumes/costume_form.html',
                  {'form': form, 'titre': 'Modifier le costume', 'costume': costume})


@login_required
@user_passes_test(is_admin)
def costume_supprimer(request, pk):
    costume = get_object_or_404(Costume, pk=pk)
    if request.method == 'POST':
        costume.delete()
        messages.success(request, 'Costume supprimé.')
        return redirect('inventaire')
    return render(request, 'costumes/costume_confirm_delete.html', {'costume': costume})


@login_required
def costume_emprunter(request, pk):
    costume = get_object_or_404(Costume, pk=pk)
    if costume.est_emprunte:
        messages.warning(request, 'Ce costume est déjà emprunté.')
        return redirect('inventaire')
    if request.method == 'POST':
        form = EmpruntForm(request.POST)
        if form.is_valid():
            acteur = form.cleaned_data['acteur']
            date = form.cleaned_data['date_emprunt']
            note = form.cleaned_data.get('note', '')
            costume.acteur = acteur
            costume.date_emprunt = date
            costume.save()
            HistoriqueEmprunt.objects.create(
                costume=costume, acteur=acteur, action='emprunt',
                date_action=date, note=note, enregistre_par=request.user
            )
            messages.success(request, f'Emprunt enregistré pour {acteur.nom_complet}.')
            return redirect('inventaire')
    else:
        form = EmpruntForm(initial={'date_emprunt': timezone.now().date()})
    return render(request, 'costumes/emprunt_form.html', {'form': form, 'costume': costume})


@login_required
@user_passes_test(is_admin)
def costume_retourner(request, pk):
    costume = get_object_or_404(Costume, pk=pk)
    if not costume.est_emprunte:
        messages.warning(request, "Ce costume n'est pas emprunté.")
        return redirect('inventaire')
    if request.method == 'POST':
        HistoriqueEmprunt.objects.create(
            costume=costume, acteur=costume.acteur, action='retour',
            date_action=timezone.now().date(),
            note=request.POST.get('note', ''),
            enregistre_par=request.user
        )
        costume.acteur = None
        costume.date_emprunt = None
        costume.save()
        messages.success(request, 'Retour enregistré avec succès.')
        return redirect('inventaire')
    return render(request, 'costumes/retour_confirm.html', {'costume': costume})


# ─── Historique ──────────────────────────────────────────────────────────────

@login_required
def historique(request):
    historiques = HistoriqueEmprunt.objects.select_related('costume__type_costume', 'acteur').all()

    if not is_admin(request.user):
        try:
            acteur_courant = Acteur.objects.get(user=request.user)
            historiques = historiques.filter(acteur=acteur_courant)
        except Acteur.DoesNotExist:
            historiques = historiques.none()

    form = FiltreHistoriqueForm(request.GET or None)
    if form.is_valid():
        if form.cleaned_data.get('date_debut'):
            historiques = historiques.filter(date_action__gte=form.cleaned_data['date_debut'])
        if form.cleaned_data.get('date_fin'):
            historiques = historiques.filter(date_action__lte=form.cleaned_data['date_fin'])
        if form.cleaned_data.get('action'):
            historiques = historiques.filter(action=form.cleaned_data['action'])
        if is_admin(request.user) and form.cleaned_data.get('acteur'):
            historiques = historiques.filter(acteur=form.cleaned_data['acteur'])

    context = {
        'historiques': historiques, 'form': form,
        'is_admin': is_admin(request.user),
    }
    return render(request, 'costumes/historique.html', context)


# ─── Dashboard Admin ─────────────────────────────────────────────────────────

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    empruntes = Costume.objects.filter(acteur__isnull=False).select_related('type_costume', 'acteur')
    if request.method == 'POST':
        costume_id = request.POST.get('costume_id')
        costume = get_object_or_404(Costume, pk=costume_id)
        if costume.est_emprunte:
            HistoriqueEmprunt.objects.create(
                costume=costume, acteur=costume.acteur, action='reset',
                date_action=timezone.now().date(),
                note='Réinitialisation par administrateur',
                enregistre_par=request.user
            )
            costume.acteur = None
            costume.date_emprunt = None
            costume.save()
            messages.success(request, 'Emprunt réinitialisé avec succès.')
        return redirect('admin_dashboard')

    context = {
        'empruntes': empruntes,
        'total': Costume.objects.count(),
        'disponibles': Costume.objects.filter(acteur__isnull=True).count(),
        'empruntes_count': empruntes.count(),
        'a_reparer': Costume.objects.filter(etat='reparer').count(),
        'types_count': TypeCostume.objects.count(),
        'acteurs_count': Acteur.objects.count(),
        'representations_count': Representation.objects.count(),
        'essayages_a_venir': Essayage.objects.filter(
            date_essayage__gte=timezone.now().date(), statut='planifie').count(),
    }
    return render(request, 'costumes/admin_dashboard.html', context)


# ─── Types & Acteurs ─────────────────────────────────────────────────────────

@login_required
@user_passes_test(is_admin)
def type_liste(request):
    return render(request, 'costumes/type_liste.html', {'types': TypeCostume.objects.all()})


@login_required
@user_passes_test(is_admin)
def type_ajouter(request):
    if request.method == 'POST':
        form = TypeCostumeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Type ajouté.')
            return redirect('type_liste')
    else:
        form = TypeCostumeForm()
    return render(request, 'costumes/type_form.html', {'form': form, 'titre': 'Ajouter un type'})


@login_required
@user_passes_test(is_admin)
def type_modifier(request, pk):
    type_obj = get_object_or_404(TypeCostume, pk=pk)
    if request.method == 'POST':
        form = TypeCostumeForm(request.POST, instance=type_obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Type modifié.')
            return redirect('type_liste')
    else:
        form = TypeCostumeForm(instance=type_obj)
    return render(request, 'costumes/type_form.html', {'form': form, 'titre': 'Modifier le type'})


@login_required
@user_passes_test(is_admin)
def type_supprimer(request, pk):
    type_obj = get_object_or_404(TypeCostume, pk=pk)
    if request.method == 'POST':
        type_obj.delete()
        messages.success(request, 'Type supprimé.')
        return redirect('type_liste')
    return render(request, 'costumes/type_confirm_delete.html', {'type_obj': type_obj})


@login_required
@user_passes_test(is_admin)
def acteur_liste(request):
    return render(request, 'costumes/acteur_liste.html', {'acteurs': Acteur.objects.all()})


@login_required
@user_passes_test(is_admin)
def acteur_ajouter(request):
    if request.method == 'POST':
        form = ActeurForm(request.POST)
        if form.is_valid():
            from django.contrib.auth.models import User as AuthUser
            acteur = form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            if username and password:
                if not AuthUser.objects.filter(username=username).exists():
                    user = AuthUser.objects.create_user(
                        username=username, password=password,
                        first_name=acteur.prenom, last_name=acteur.nom)
                    acteur.user = user
                    acteur.save()
                    messages.success(request, f'Acteur ajouté. Login : {username} / MDP : {password}')
                else:
                    messages.warning(request, f'Acteur ajouté, mais "{username}" existe déjà.')
            else:
                messages.success(request, 'Acteur ajouté (sans compte utilisateur).')
            return redirect('acteur_liste')
    else:
        form = ActeurForm()
    return render(request, 'costumes/acteur_form.html', {'form': form, 'titre': 'Ajouter un acteur'})


@login_required
@user_passes_test(is_admin)
def acteur_modifier(request, pk):
    acteur = get_object_or_404(Acteur, pk=pk)
    if request.method == 'POST':
        form = ActeurForm(request.POST, instance=acteur)
        if form.is_valid():
            from django.contrib.auth.models import User as AuthUser
            acteur = form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            if username:
                if acteur.user:
                    # ✅ FIX: mise à jour propre du username + password optionnel
                    acteur.user.username = username
                    if password:
                        acteur.user.set_password(password)
                    acteur.user.first_name = acteur.prenom
                    acteur.user.last_name = acteur.nom
                    acteur.user.save()
                    messages.success(request, f'Acteur modifié. Compte mis à jour : {username}')
                else:
                    if not AuthUser.objects.filter(username=username).exists():
                        user = AuthUser.objects.create_user(
                            username=username, password=password,
                            first_name=acteur.prenom, last_name=acteur.nom)
                        acteur.user = user
                        acteur.save()
                        messages.success(request, f'Acteur modifié. Login : {username}')
                    else:
                        messages.warning(request, f'Acteur modifié, mais "{username}" existe déjà.')
            else:
                messages.success(request, 'Acteur modifié.')
            return redirect('acteur_liste')
    else:
        form = ActeurForm(instance=acteur)
    return render(request, 'costumes/acteur_form.html', {'form': form, 'titre': "Modifier l'acteur"})


@login_required
@user_passes_test(is_admin)
def acteur_supprimer(request, pk):
    acteur = get_object_or_404(Acteur, pk=pk)
    if request.method == 'POST':
        acteur.delete()
        messages.success(request, 'Acteur supprimé.')
        return redirect('acteur_liste')
    return render(request, 'costumes/acteur_confirm_delete.html', {'acteur': acteur})


# ─── NOUVEAU : Représentations ────────────────────────────────────────────────

@login_required
@user_passes_test(is_admin)
def representation_liste(request):
    representations = Representation.objects.prefetch_related('essayages').all()
    return render(request, 'costumes/representation_liste.html', {
        'representations': representations,
        'is_admin': is_admin(request.user),
    })


@login_required
@user_passes_test(is_admin)
def representation_ajouter(request):
    if request.method == 'POST':
        form = RepresentationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Représentation ajoutée.')
            return redirect('representation_liste')
    else:
        form = RepresentationForm()
    return render(request, 'costumes/representation_form.html',
                  {'form': form, 'titre': 'Ajouter une représentation'})


@login_required
@user_passes_test(is_admin)
def representation_modifier(request, pk):
    rep = get_object_or_404(Representation, pk=pk)
    if request.method == 'POST':
        form = RepresentationForm(request.POST, instance=rep)
        if form.is_valid():
            form.save()
            messages.success(request, 'Représentation modifiée.')
            return redirect('representation_liste')
    else:
        form = RepresentationForm(instance=rep)
    return render(request, 'costumes/representation_form.html',
                  {'form': form, 'titre': 'Modifier la représentation', 'rep': rep})


@login_required
@user_passes_test(is_admin)
def representation_supprimer(request, pk):
    rep = get_object_or_404(Representation, pk=pk)
    if request.method == 'POST':
        rep.delete()
        messages.success(request, 'Représentation supprimée.')
        return redirect('representation_liste')
    return render(request, 'costumes/representation_confirm_delete.html', {'rep': rep})


@login_required
@user_passes_test(is_admin)
def representation_detail(request, pk):
    rep = get_object_or_404(Representation, pk=pk)
    essayages = rep.essayages.select_related('acteur', 'costume').all()
    return render(request, 'costumes/representation_detail.html', {
        'rep': rep, 'essayages': essayages,
        'is_admin': is_admin(request.user),
    })


# ─── NOUVEAU : Essayages ──────────────────────────────────────────────────────

@login_required
def essayage_liste(request):
    if is_admin(request.user):
        essayages = Essayage.objects.select_related('representation', 'acteur', 'costume').all()
    else:
        try:
            acteur_courant = Acteur.objects.get(user=request.user)
            essayages = Essayage.objects.filter(acteur=acteur_courant).select_related(
                'representation', 'acteur', 'costume')
        except Acteur.DoesNotExist:
            essayages = Essayage.objects.none()

    form = FiltreEssayageForm(request.GET or None)
    if form.is_valid():
        if form.cleaned_data.get('representation') and is_admin(request.user):
            essayages = essayages.filter(representation=form.cleaned_data['representation'])
        if form.cleaned_data.get('acteur') and is_admin(request.user):
            essayages = essayages.filter(acteur=form.cleaned_data['acteur'])
        if form.cleaned_data.get('statut'):
            essayages = essayages.filter(statut=form.cleaned_data['statut'])
        if form.cleaned_data.get('date_debut'):
            essayages = essayages.filter(date_essayage__gte=form.cleaned_data['date_debut'])
        if form.cleaned_data.get('date_fin'):
            essayages = essayages.filter(date_essayage__lte=form.cleaned_data['date_fin'])

    context = {
        'essayages': essayages, 'form': form,
        'is_admin': is_admin(request.user),
    }
    return render(request, 'costumes/essayage_liste.html', context)


@login_required
@user_passes_test(is_admin)
def essayage_ajouter(request):
    initial = {}
    if request.GET.get('representation'):
        initial['representation'] = request.GET['representation']
    if request.method == 'POST':
        form = EssayageForm(request.POST)
        if form.is_valid():
            essayage = form.save(commit=False)
            essayage.enregistre_par = request.user
            essayage.save()
            messages.success(request, 'Essayage planifié.')
            return redirect('essayage_liste')
    else:
        form = EssayageForm(initial=initial)
    return render(request, 'costumes/essayage_form.html',
                  {'form': form, 'titre': 'Planifier un essayage'})


@login_required
@user_passes_test(is_admin)
def essayage_modifier(request, pk):
    essayage = get_object_or_404(Essayage, pk=pk)
    if request.method == 'POST':
        form = EssayageForm(request.POST, instance=essayage)
        if form.is_valid():
            form.save()
            messages.success(request, 'Essayage modifié.')
            return redirect('essayage_liste')
    else:
        form = EssayageForm(instance=essayage)
    return render(request, 'costumes/essayage_form.html',
                  {'form': form, 'titre': "Modifier l'essayage", 'essayage': essayage})


@login_required
@user_passes_test(is_admin)
def essayage_supprimer(request, pk):
    essayage = get_object_or_404(Essayage, pk=pk)
    if request.method == 'POST':
        essayage.delete()
        messages.success(request, 'Essayage supprimé.')
        return redirect('essayage_liste')
    return render(request, 'costumes/essayage_confirm_delete.html', {'essayage': essayage})


@login_required
@user_passes_test(is_admin)
def essayage_changer_statut(request, pk):
    """Change rapide de statut via bouton."""
    essayage = get_object_or_404(Essayage, pk=pk)
    nouveau_statut = request.POST.get('statut')
    if nouveau_statut in dict(Essayage.STATUT_CHOICES):
        essayage.statut = nouveau_statut
        essayage.save()
        messages.success(request, f'Statut mis à jour : {essayage.get_statut_display()}')
    return redirect('essayage_liste')
