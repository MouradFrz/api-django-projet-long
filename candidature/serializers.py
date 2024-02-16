from django.utils import timezone
from rest_framework import serializers, status
from rest_framework.fields import SerializerMethodField
from rest_framework.response import Response
from authentification.models import User
from authentification.serializers import UserSerializer

from candidature.models import Candidature, FichierUtilisateur
from formations.serializers import FormationSerializer


class CreateCandidatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidature
        fields = [
            "id",
            "idformation",
            "etat",
            "lettre_de_motiv",
            "idcandidat",
            "date_envoi",
        ]
        read_only_fields = ["etat", "date_envoi"]

    def create(self, validated_data):
        validated_data["etat"] = "sent"
        validated_data["date_envoi"] = timezone.now()
        return super().create(validated_data)


class FichierUtilisateurSerializer(serializers.ModelSerializer):
    class Meta:
        model = FichierUtilisateur
        fields = ["id", "titre", "url", "date_upload"]


class UploadFichierUtilisateurSerializer(serializers.ModelSerializer):
    class Meta:
        model = FichierUtilisateur
        fields = ["titre", "url", "date_upload", "idutilisateur"]


class SimpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["nom", "prenom"]


class CandidatureSerializer(serializers.ModelSerializer):
    candidat = SimpleUserSerializer(source="idcandidat")

    class Meta:
        model = Candidature
        fields = ["id", "date_envoi", "etat", "idformation", "candidat"]


class UserWithDocumentsSerializer(serializers.ModelSerializer):
    documents = SerializerMethodField()

    class Meta:
        model = User
        fields = ["nom", "prenom", "titre", "pfp", "documents"]

    def get_documents(self, user):
        fichiers = FichierUtilisateur.objects.filter(idutilisateur=user.id)
        return FichierUtilisateurSerializer(fichiers, many=True).data


class CandidatureFormationSerializer(serializers.ModelSerializer):
    formation = FormationSerializer(source="idformation")

    class Meta:
        model = Candidature
        fields = ["date_envoi", "etat", "formation", "lettre_de_motiv"]


class FullCandidatureSerializer(serializers.ModelSerializer):
    etudiant = UserWithDocumentsSerializer(source="idcandidat")

    class Meta:
        model = Candidature
        fields = ["date_envoi", "etat", "idformation", "lettre_de_motiv", "etudiant"]
