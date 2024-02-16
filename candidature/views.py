import os
from django.db import IntegrityError
from django.core.files.storage import default_storage
from django.http import FileResponse
from rest_framework import status
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.fields import ObjectDoesNotExist
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from authentification.permission import IsEnseignant, IsEtudiant

from candidature.models import Candidature, FichierUtilisateur
from candidature.serializers import (
    CandidatureFormationSerializer,
    CandidatureSerializer,
    CreateCandidatureSerializer,
    FichierUtilisateurSerializer,
    FullCandidatureSerializer,
    UploadFichierUtilisateurSerializer,
)
from formations.models import Formation

# Create your views here.


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsEtudiant])
def get_user_docs(request):
    docs = FichierUtilisateur.objects.filter(idutilisateur=request.user.id)
    serializer = FichierUtilisateurSerializer(docs, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsEtudiant])
def upload_fichier(request):
    data = request.data.copy()
    data["idutilisateur"] = request.user.id
    serializer = UploadFichierUtilisateurSerializer(data=data)
    if serializer.is_valid(raise_exception=True):
        serializer.save()
    return Response(status=status.HTTP_201_CREATED)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated, IsEtudiant])
def supprimier_fichier(request, id):
    try:
        fichier = FichierUtilisateur.objects.get(id=id)
    except FichierUtilisateur.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    default_storage.delete(fichier.url.path)
    fichier.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsEtudiant])
def get_candidatures(request):
    candidatures = Candidature.objects.filter(idcandidat=request.user.id)
    serializer = CandidatureFormationSerializer(candidatures, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
@authentication_classes([])
def telecharger_fichier(request, fichier_id):
    fichier = get_object_or_404(FichierUtilisateur, pk=fichier_id)
    response = FileResponse(open(fichier.url.path, "rb"))
    response[
        "Content-Disposition"
    ] = f'attachment; filename="{os.path.basename(str(fichier.url))}"'
    return response


@api_view(["DELETE"])
@permission_classes([IsAuthenticated, IsEtudiant])
def supprimer_candidature(request, id):
    try:
        candidature = Candidature.objects.get(id=id)
    except Candidature.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if candidature.idcandidat_id != request.user.id:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    candidature.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsEnseignant])
def get_candidature_ens(request, id):
    try:
        candidature = Candidature.objects.get(id=id)
    except Candidature.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    try:
        formation = request.user.formation
    except ObjectDoesNotExist:
        return Response(
            "Vous n'avez pas de formation.", status=status.HTTP_404_NOT_FOUND
        )
    if candidature.idformation != formation:
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    serializer = FullCandidatureSerializer(candidature)

    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["PATCH"])
@permission_classes([IsAuthenticated, IsEnseignant])
def accepter_candidature(request, id):
    try:
        candidature = Candidature.objects.get(id=id)
    except Candidature.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    try:
        formation = request.user.formation
    except ObjectDoesNotExist:
        return Response(
            "Vous n'avez pas de formation.", status=status.HTTP_404_NOT_FOUND
        )
    if candidature.idformation != formation:
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    user = candidature.idcandidat
    user.inscrit_a = formation
    user.save()
    candidature.etat = "Accepté"
    candidature.save()
    return Response(status=status.HTTP_200_OK)


@api_view(["PATCH"])
@permission_classes([IsAuthenticated, IsEnseignant])
def refuser_candidature(request, id):
    try:
        candidature = Candidature.objects.get(id=id)
    except Candidature.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    try:
        formation = request.user.formation
    except ObjectDoesNotExist:
        return Response(
            "Vous n'avez pas de formation.", status=status.HTTP_404_NOT_FOUND
        )
    if candidature.idformation != formation:
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    candidature.etat = "Refusé"
    candidature.save()
    return Response(status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsEnseignant])
def get_candidatures_ens(request):
    try:
        formation = Formation.objects.get(responsable=request.user)
    except Formation.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    candidatures = Candidature.objects.filter(idformation=formation).order_by(
        "date_envoi"
    )
    serializer = CandidatureSerializer(candidatures, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsEtudiant])
def envoyer_candidature(request, idformation):
    get_object_or_404(Formation, id=idformation)
    try:
        mutable_initial_data = request.data.copy()
        mutable_initial_data["idcandidat"] = request.user.id
        mutable_initial_data["idformation"] = idformation
        serializer = CreateCandidatureSerializer(data=mutable_initial_data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)
    except IntegrityError:
        return Response(status=status.HTTP_400_BAD_REQUEST)
