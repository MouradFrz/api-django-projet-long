# views.py
from django.contrib import messages
from django.core.files.storage import default_storage
from django.http import FileResponse
from rest_framework import viewsets
from yaml import serialize
from .models import FichierChapitre, Formation, Module, Chapitre
from .serializers import (
    FormationCompleteSerializer,
    FormationSerializer,
    ModuleSerializer,
    ChapitreSerializer,
    AjouterModuleSerializer,
    SimpleUserSerializer,
    UploadFichierChapitreSerializer,
)
from .permissions import IsEnseignant, IsReferent
from django.shortcuts import render, get_object_or_404, redirect
from .forms import FormationForm, ModuleForm, ChapitreForm
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from authentification.models import User
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)


@api_view(["GET"])
def liste_formations(request):
    formations = Formation.objects.all()
    serializer = FormationSerializer(formations, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([IsEnseignant])
def ajouter_formation(request):
    serializer = FormationSerializer(data=request.data)

    if serializer.is_valid(raise_exception=True):
        serializer.save(responsable=request.user)
        messages.success(request, "Formation ajoutée avec succès.")
        return Response(
            {"success": "Formation ajoutée avec succès."},
            status=status.HTTP_201_CREATED,
        )

    return Response(status=status.HTTP_200_OK)


@api_view(["GET"])
def formation(request, id):
    formation = get_object_or_404(Formation, pk=id)
    serializer = FormationCompleteSerializer(formation)
    return Response(serializer.data, status=200)


@api_view(["PATCH"])
@permission_classes([IsEnseignant])
def modifier_formation(request, formation_id):
    formation = get_object_or_404(Formation, pk=formation_id)
    if formation.responsable != request.user:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    serializer = FormationSerializer(formation, data=request.data)
    if serializer.is_valid(raise_exception=True):
        serializer.save()
        return Response(
            {"success": "Formation modifiée avec succès."}, status=status.HTTP_200_OK
        )

    return Response(
        {"formation": FormationSerializer(formation).data}, status=status.HTTP_200_OK
    )


@api_view(["DELETE"])
@permission_classes([IsEnseignant])
def supprimer_formation(request, formation_id):
    formation = get_object_or_404(Formation, pk=formation_id)
    if formation.responsable != request.user:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    formation.delete()
    return Response(
        {"success": "Formation supprimée avec succès."}, status=status.HTTP_200_OK
    )


@api_view(["GET"])
def liste_modules(request, formation_id):
    get_object_or_404(Formation, pk=formation_id)
    modules = Module.objects.filter(formation_id=formation_id)
    serializer = ModuleSerializer(modules, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
def module_complet(request, module_id):
    module = get_object_or_404(Module, pk=module_id)
    serializer = ModuleSerializer(module)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated, IsEnseignant])
def supprimer_fichier(request, id):
    try:
        fichier = FichierChapitre.objects.get(id=id)
    except FichierChapitre.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    default_storage.delete(fichier.url.path)
    fichier.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["GET"])
@permission_classes([IsEnseignant])
def list_module_pour_ens(request):
    modules = Module.objects.filter(responsable=request.user)
    serializer = ModuleSerializer(data=modules, many=True)
    serializer.is_valid()
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([IsEnseignant])
def ajouter_module(request):
    formation = get_object_or_404(Formation, responsable=request.user.id)
    serializer = AjouterModuleSerializer(data=request.data)
    if formation.responsable != request.user:
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    if serializer.is_valid(raise_exception=True):
        serializer.save(formation=formation)
        messages.success(request, "Module ajouté avec succès.")
        return Response(
            {"success": "Module ajouté avec succès."}, status=status.HTTP_201_CREATED
        )


@api_view(["PATCH"])
@permission_classes([IsEnseignant])
def set_responsable(request, id):
    module = get_object_or_404(Module, id=id)
    try:
        user = User.objects.get(email=request.data["email"])
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    except KeyError:
        return Response(status=status.HTTP_404_NOT_FOUND)
    module.responsable = user
    module.save()
    return Response(
        {"success": "Module modifié avec succes"}, status=status.HTTP_200_OK
    )


@api_view(["POST"])
# @permission_classes([IsEnseignant])
def ajouter_fichier(request, chapitre_id):
    get_object_or_404(Chapitre, pk=chapitre_id)
    myfile = request.FILES.get("url")
    if myfile:
        data = request.data.copy()
        data["chapitre"] = chapitre_id
        data["titre"] = myfile.name
        data["url"] = myfile
        serializer = UploadFichierChapitreSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response(status=status.HTTP_201_CREATED)
    return Response(status=404)


@api_view(["GET"])
@permission_classes([IsEnseignant])
def get_etudiants_de_ma_formation(request):
    formation = Formation.objects.filter(responsable=request.user).first()
    if not formation:
        return Response(
            {"detail": "Teacher does not have a formation."},
            status=status.HTTP_404_NOT_FOUND,
        )
    etudiants = User.objects.filter(inscrit_a=formation).all()
    serializer = SimpleUserSerializer(data=etudiants, many=True)
    serializer.is_valid()
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
@authentication_classes([])
def telecharger_fichier(request, fichier_id):
    fichier = get_object_or_404(FichierChapitre, pk=fichier_id)
    response = FileResponse(open(fichier.url.path, "rb"))
    response["Content-Disposition"] = f'attachment; filename="{fichier.titre}"'
    return response


@api_view(["PATCH"])
@permission_classes([IsEnseignant])
def modifier_module(request, module_id, formation_id):
    module = get_object_or_404(Module, id=module_id)
    serializer = ModuleSerializer(module, data=request.data)
    if serializer.is_valid(raise_exception=True):
        serializer.save()
        return Response(
            {"success": "Module modifié avec succès."}, status=status.HTTP_200_OK
        )


@api_view(["DELETE"])
@permission_classes([IsEnseignant])
def supprimer_module(request, module_id):
    module = get_object_or_404(Module, id=module_id)
    module.delete()
    return Response(
        {"success": "Module supprimé avec succès."}, status=status.HTTP_200_OK
    )


@api_view(["GET"])
def liste_chapitres(request, module_id):
    chapitres = Chapitre.objects.filter(module_id=module_id)
    serializer = ChapitreSerializer(chapitres, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([IsEnseignant])
def ajouter_chapitre(request, module_id):
    module = get_object_or_404(Module, id=module_id)

    serializer = ChapitreSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        serializer.save(module=module)
        messages.success(request, "Chapitre ajouté avec succès.")
        return Response(
            {"success": "Chapitre ajouté avec succès."}, status=status.HTTP_201_CREATED
        )


@api_view(["PATCH"])
@permission_classes([IsEnseignant])
def modifier_chapitre(request, module_id, chapitre_id):
    chapitre = get_object_or_404(Chapitre, id=chapitre_id)

    serializer = ChapitreSerializer(chapitre, data=request.data)
    if serializer.is_valid(raise_exception=True):
        serializer.save()
        return Response(
            {"success": "Chapitre modifié avec succès."}, status=status.HTTP_200_OK
        )

    return Response(
        {"chapitre": ChapitreSerializer(chapitre).data}, status=status.HTTP_200_OK
    )


@api_view(["DELETE"])
@permission_classes([IsEnseignant])
def supprimer_chapitre(request, chapitre_id):
    chapitre = get_object_or_404(Chapitre, id=chapitre_id)

    chapitre.delete()
    return Response(
        {"success": "Chapitre supprimé avec succès."}, status=status.HTTP_200_OK
    )
