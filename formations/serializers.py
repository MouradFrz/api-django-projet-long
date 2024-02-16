# serializers.py

from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from authentification.models import User


from .models import FichierChapitre, Formation, Module, Chapitre


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["nom", "prenom", "email"]


class FormationSerializer(serializers.ModelSerializer):
    responsable = UserSerializer(required=False)

    class Meta:
        model = Formation
        fields = "__all__"


class FormationCompleteSerializer(serializers.ModelSerializer):
    responsable = UserSerializer(required=False)
    modules = SerializerMethodField()

    def get_modules(self, obj):
        modules = Module.objects.filter(formation=obj)
        serializer = ModuleSerializer(modules, many=True)
        return serializer.data

    class Meta:
        model = Formation
        fields = "__all__"


class SimpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["nom", "prenom", "pfp"]


class FichierChapitreSerializer(serializers.ModelSerializer):
    class Meta:
        model = FichierChapitre
        fields = "__all__"


class ChapitreSerializer(serializers.ModelSerializer):
    fichiers = SerializerMethodField()

    def get_fichiers(self, chapitre):
        fichiers = FichierChapitre.objects.filter(chapitre=chapitre.id)
        return FichierChapitreSerializer(fichiers, many=True).data

    class Meta:
        model = Chapitre
        fields = "__all__"


class UploadFichierChapitreSerializer(serializers.ModelSerializer):
    class Meta:
        model = FichierChapitre
        fields = ["titre", "url", "date_upload", "chapitre"]


class ModuleSerializer(serializers.ModelSerializer):
    chapitres = ChapitreSerializer(many=True)
    responsable = UserSerializer()

    class Meta:
        model = Module
        fields = "__all__"


class AjouterModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = ["nom", "description", "formation", "responsable"]
