from rest_framework.permissions import BasePermission


class IsEtudiant(BasePermission):
    def has_permission(self, request, view):
        return True if request.user.type == "etudiant" else False


class IsEnseignant(BasePermission):
    def has_permission(self, request, view):
        return True if request.user.type == "enseignant" else False


class IsReferent(BasePermission):
    def has_permission(self, request, view):
        return True if request.user.type == "referent" else False


class IsInactive(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_active
