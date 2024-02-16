# models.py

from django.utils import timezone
from django.db import models

# from authentification.models import User


class Formation(models.Model):
    nom = models.CharField(max_length=255)
    description = models.TextField()
    date_debut = models.DateField(default=None, null=True)
    date_fin = models.DateField(default=None, null=True)
    nombre_etudiants = models.IntegerField(default=0)
    debouches_professionnels = models.TextField(default="")
    responsable = models.OneToOneField(
        "authentification.User", on_delete=models.CASCADE, default=None
    )

    def __str__(self):
        return self.nom


class Module(models.Model):
    nom = models.CharField(max_length=100)
    description = models.TextField()
    formation = models.ForeignKey(Formation, on_delete=models.CASCADE, default=None)

    responsable = models.ForeignKey(
        "authentification.User", on_delete=models.CASCADE, default=None, null=True
    )


class Chapitre(models.Model):
    module = models.ForeignKey(
        Module, related_name="chapitres", on_delete=models.CASCADE, default=None
    )
    nom = models.CharField(max_length=100)
    description = models.TextField()


class FichierChapitre(models.Model):
    chapitre = models.ForeignKey(Chapitre, on_delete=models.CASCADE)
    titre = models.CharField(max_length=80)
    url = models.FileField(upload_to="chapitres/")
    date_upload = models.DateField(default=timezone.now)
