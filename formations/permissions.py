from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsEtudiant(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.type == "etudiant"

class IsEnseignant(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.type == "enseignant"

class IsReferent(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.type == "referent"
