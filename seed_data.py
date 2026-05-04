"""
Script de création des données initiales (seed).
Exécuter avec : python manage.py shell < seed_data.py
Ou directement : python seed_data.py (depuis le dossier du projet)
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'theaterwardrobe.settings')
django.setup()

from django.contrib.auth.models import User
from costumes.models import TypeCostume, Acteur, Costume

print("=== Création des données initiales ===\n")

# 1. Comptes utilisateurs
print("1. Création des utilisateurs...")
if not User.objects.filter(username='admin').exists():
    admin = User.objects.create_superuser('admin', 'admin@theater.fr', 'admin123',
                                          first_name='Admin', last_name='Régisseur')
    print("   ✓ admin / admin123 (superuser)")
else:
    print("   - admin existe déjà")

if not User.objects.filter(username='acteur1').exists():
    user1 = User.objects.create_user('acteur1', 'marie@theater.fr', 'acteur123',
                                     first_name='Marie', last_name='Dupont')
    print("   ✓ acteur1 / acteur123 (acteur)")
else:
    print("   - acteur1 existe déjà")

if not User.objects.filter(username='acteur2').exists():
    user2 = User.objects.create_user('acteur2', 'jean@theater.fr', 'acteur123',
                                     first_name='Jean', last_name='Martin')
    print("   ✓ acteur2 / acteur123 (acteur)")
else:
    print("   - acteur2 existe déjà")

# 2. Types de costumes
print("\n2. Création des types de costumes...")
types_data = [
    ('Robe de bal', 'Baroque / XVIIIe'),
    ('Armure complète', 'Médiéval'),
    ('Chapeau de sorcier', 'Fantastique'),
    ('Manteau noble', 'Renaissance'),
    ('Robe paysanne', 'Médiéval'),
    ('Costume de bouffon', 'Baroque'),
    ('Toge romaine', 'Antiquité'),
    ('Kimono', 'Asie traditionnelle'),
    ('Frac de cérémonie', 'XIXe siècle'),
    ('Robe empire', 'Empire / Napoléonien'),
]
type_objs = {}
for libelle, epoque in types_data:
    t, created = TypeCostume.objects.get_or_create(libelle=libelle, defaults={'epoque': epoque})
    type_objs[libelle] = t
    if created:
        print(f"   ✓ {libelle}")

# 3. Acteurs (avec liaison user)
print("\n3. Création des acteurs...")

# Récupérer les users créés (ou existants)
user1 = User.objects.get(username='acteur1')
user2 = User.objects.get(username='acteur2')

acteurs_data = [
    ('Dupont', 'Marie', 'Poitrine: 90cm, Taille: 68cm, Hanches: 96cm', user1),
    ('Martin', 'Jean', 'Épaules: 48cm, Poitrine: 102cm, Taille: 88cm', user2),
    ('Blanc', 'Pierre', 'Taille: 82cm, Hanches: 92cm', None),
    ('Léa', 'Sophie', 'Poitrine: 86cm, Taille: 64cm, Hanches: 90cm', None),
    ('Bernard', 'Louis', 'Épaules: 50cm, Poitrine: 108cm', None),
]
acteur_objs = {}
for nom, prenom, mensurations, user in acteurs_data:
    a, created = Acteur.objects.get_or_create(nom=nom, prenom=prenom,
                                               defaults={'mensurations': mensurations})
    # Relier le user à l'acteur
    if user and a.user != user:
        a.user = user
        a.save()
        print(f"   ✓ {prenom} {nom} → lié à {user.username}")
    elif created:
        print(f"   ✓ {prenom} {nom}")
    acteur_objs[f"{prenom} {nom}"] = a

# 4. Costumes
print("\n4. Création des costumes...")
costumes_data = [
    ('Robe de bal', 'bordeaux', 'm', 'bon', 'Robe de soirée brodée or, état général bon'),
    ('Armure complète', 'noir', 'l', 'reparer', 'Rivets manquants sur l\'épaulière gauche'),
    ('Chapeau de sorcier', 'violet', 'm', 'neuf', 'Jamais porté, étoiles argentées'),
    ('Manteau noble', 'bleu', 'xl', 'bon', 'Velours bleu nuit, broderies dorées'),
    ('Robe paysanne', 'vert', 's', 'use', 'Tissu usé aux coudes, à repeindre'),
    ('Costume de bouffon', 'or', 'm', 'bon', 'Grelots intacts, multicolore'),
    ('Toge romaine', 'blanc', 'l', 'bon', 'Lin blanc, ceinture incluse'),
    ('Kimono', 'rouge', 'm', 'neuf', 'Soie traditionnelle, motifs floraux'),
    ('Frac de cérémonie', 'noir', 'm', 'bon', 'Queue de pie, boutons nacre'),
    ('Robe empire', 'blanc', 's', 'reparer', 'Couture au niveau de l\'emmanchure à refaire'),
]
for libelle, couleur, taille, etat, desc in costumes_data:
    if not Costume.objects.filter(type_costume=type_objs[libelle], couleur=couleur).exists():
        Costume.objects.create(
            type_costume=type_objs[libelle],
            couleur=couleur, taille=taille, etat=etat, description=desc
        )
        print(f"   ✓ {libelle} ({couleur})")

# 5. Simuler quelques emprunts
print("\n5. Simulation d'emprunts...")
from costumes.models import HistoriqueEmprunt
from django.utils import timezone
import datetime

admin_user = User.objects.get(username='admin')
a_martin = acteur_objs.get('Jean Martin')
a_blanc = acteur_objs.get('Pierre Blanc')

c1 = Costume.objects.filter(type_costume__libelle='Manteau noble').first()
c2 = Costume.objects.filter(type_costume__libelle='Costume de bouffon').first()

if c1 and a_martin and not c1.acteur:
    date_emprunt = datetime.date.today() - datetime.timedelta(days=5)
    c1.acteur = a_martin
    c1.date_emprunt = date_emprunt
    c1.save()
    HistoriqueEmprunt.objects.create(
        costume=c1, acteur=a_martin, action='emprunt',
        date_action=date_emprunt, note='Pour répétition acte II',
        enregistre_par=admin_user
    )
    print(f"   ✓ Manteau noble → Jean Martin")

if c2 and a_blanc and not c2.acteur:
    date_emprunt = datetime.date.today() - datetime.timedelta(days=2)
    c2.acteur = a_blanc
    c2.date_emprunt = date_emprunt
    c2.save()
    HistoriqueEmprunt.objects.create(
        costume=c2, acteur=a_blanc, action='emprunt',
        date_action=date_emprunt, note='Spectacle du vendredi',
        enregistre_par=admin_user
    )
    print(f"   ✓ Costume de bouffon → Pierre Blanc")

print("\n=== ✅ Données initialisées avec succès ! ===")
print("\nComptes disponibles :")
print("  admin     / admin123   → Régisseur (accès complet)")
print("  acteur1   / acteur123  → Acteur Marie Dupont")
print("  acteur2   / acteur123  → Acteur Jean Martin")
print("\nLancer le serveur : python manage.py runserver")
print("Accès : http://127.0.0.1:8000/")
