from django.urls import path
from . import views

urlpatterns = [
    # Inventaire
    path('', views.inventaire, name='inventaire'),
    path('costumes/ajouter/', views.costume_ajouter, name='costume_ajouter'),
    path('costumes/<int:pk>/modifier/', views.costume_modifier, name='costume_modifier'),
    path('costumes/<int:pk>/supprimer/', views.costume_supprimer, name='costume_supprimer'),
    path('costumes/<int:pk>/emprunter/', views.costume_emprunter, name='costume_emprunter'),
    path('costumes/<int:pk>/retourner/', views.costume_retourner, name='costume_retourner'),

    # Historique
    path('historique/', views.historique, name='historique'),

    # Admin dashboard
    path('administration/', views.admin_dashboard, name='admin_dashboard'),

    # Types de costumes
    path('types/', views.type_liste, name='type_liste'),
    path('types/ajouter/', views.type_ajouter, name='type_ajouter'),
    path('types/<int:pk>/modifier/', views.type_modifier, name='type_modifier'),
    path('types/<int:pk>/supprimer/', views.type_supprimer, name='type_supprimer'),

    # Acteurs
    path('acteurs/', views.acteur_liste, name='acteur_liste'),
    path('acteurs/ajouter/', views.acteur_ajouter, name='acteur_ajouter'),
    path('acteurs/<int:pk>/modifier/', views.acteur_modifier, name='acteur_modifier'),
    path('acteurs/<int:pk>/supprimer/', views.acteur_supprimer, name='acteur_supprimer'),

    # NOUVEAU : Représentations
    path('representations/', views.representation_liste, name='representation_liste'),
    path('representations/ajouter/', views.representation_ajouter, name='representation_ajouter'),
    path('representations/<int:pk>/', views.representation_detail, name='representation_detail'),
    path('representations/<int:pk>/modifier/', views.representation_modifier, name='representation_modifier'),
    path('representations/<int:pk>/supprimer/', views.representation_supprimer, name='representation_supprimer'),

    # NOUVEAU : Essayages
    path('essayages/', views.essayage_liste, name='essayage_liste'),
    path('essayages/ajouter/', views.essayage_ajouter, name='essayage_ajouter'),
    path('essayages/<int:pk>/modifier/', views.essayage_modifier, name='essayage_modifier'),
    path('essayages/<int:pk>/supprimer/', views.essayage_supprimer, name='essayage_supprimer'),
    path('essayages/<int:pk>/statut/', views.essayage_changer_statut, name='essayage_changer_statut'),
]
