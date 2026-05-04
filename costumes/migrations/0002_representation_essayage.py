from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('costumes', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Representation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titre', models.CharField(max_length=200, verbose_name='Titre de la pièce')),
                ('description', models.TextField(blank=True, verbose_name='Description')),
                ('date_debut', models.DateField(verbose_name='Date de début')),
                ('date_fin', models.DateField(verbose_name='Date de fin')),
                ('lieu', models.CharField(blank=True, max_length=200, verbose_name='Lieu')),
                ('statut', models.CharField(choices=[('planifiee', 'Planifiée'), ('en_cours', 'En cours'), ('terminee', 'Terminée'), ('annulee', 'Annulée')], default='planifiee', max_length=15, verbose_name='Statut')),
                ('date_creation', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Représentation',
                'verbose_name_plural': 'Représentations',
                'ordering': ['-date_debut'],
            },
        ),
        migrations.CreateModel(
            name='Essayage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_essayage', models.DateField(verbose_name="Date de l'essayage")),
                ('heure', models.TimeField(blank=True, null=True, verbose_name='Heure')),
                ('statut', models.CharField(choices=[('planifie', 'Planifié'), ('confirme', 'Confirmé'), ('annule', 'Annulé')], default='planifie', max_length=10, verbose_name='Statut')),
                ('notes', models.TextField(blank=True, verbose_name='Notes / Ajustements')),
                ('date_creation', models.DateTimeField(auto_now_add=True)),
                ('acteur', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='essayages', to='costumes.acteur', verbose_name='Acteur')),
                ('costume', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='essayages', to='costumes.costume', verbose_name='Costume essayé')),
                ('enregistre_par', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Enregistré par')),
                ('representation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='essayages', to='costumes.representation', verbose_name='Représentation')),
            ],
            options={
                'verbose_name': 'Essayage',
                'verbose_name_plural': 'Essayages',
                'ordering': ['date_essayage', 'heure'],
            },
        ),
    ]
