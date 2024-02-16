from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser
from django.db import models
from formations.models import Formation


# Create your models here.
class User(AbstractBaseUser):
    nom = models.CharField(max_length=100, null=True)
    prenom = models.CharField(max_length=100, null=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128, null=True)
    titre = models.CharField(max_length=5, null=True)
    type = models.CharField(max_length=20, null=True)
    naissance = models.DateField(null=True)
    validated_at = models.DateField(null=True)
    pfp = models.FileField(upload_to="pfps/", null=True, default=None)
    objects = BaseUserManager()
    inscrit_a = models.ForeignKey(
        "formations.Formation", on_delete=models.CASCADE, default=None, null=True
    )
    USERNAME_FIELD = "email"
