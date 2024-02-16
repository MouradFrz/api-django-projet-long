from django.db import models
from django.utils import timezone

from authentification.models import User
from formations.models import Formation

# Create your models here.


class Candidature(models.Model):
    idcandidat = models.ForeignKey(User, on_delete=models.CASCADE)
    idformation = models.ForeignKey(Formation, on_delete=models.CASCADE)
    etat = models.CharField(max_length=15)
    lettre_de_motiv = models.TextField(null=True)
    date_envoi = models.DateField(default=timezone.now)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["idcandidat", "idformation"],
                name="unique_candidat_formation",
            )
        ]


class FichierUtilisateur(models.Model):
    idutilisateur = models.ForeignKey(User, on_delete=models.CASCADE)
    titre = models.CharField(max_length=80)
    url = models.FileField(upload_to="utilisateur/")
    date_upload = models.DateField(default=timezone.now)
