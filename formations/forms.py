# forms.py
from django import forms
from .models import Formation, Module, Chapitre


class ModuleForm(forms.ModelForm):
    class Meta:
        model = Module
        fields = ["nom", "description"]


class FormationForm(forms.ModelForm):
    class Meta:
        model = Formation
        fields = [
            "nom",
            "description",
            "date_debut",
            "date_fin",
            "nombre_etudiants",
            "debouches_professionnels",
        ]


class ChapitreForm(forms.ModelForm):
    class Meta:
        model = Chapitre
        fields = ["nom", "description"]
        widgets = {
            "fichier": forms.FileInput(attrs={"accept": "application/pdf,image/*"}),
        }
