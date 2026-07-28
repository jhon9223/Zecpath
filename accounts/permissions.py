from rest_framework.permissions import BasePermission
from .models import User


class IsAdmin(BasePermission):
    """
    Allows access only to admin users.
    """

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and User.ADMIN
        )


class IsEmployer(BasePermission):
    """
    Allows access only to employer users.
    """

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and
            request.user.role == User.EMPLOYER
        )


class IsCandidate(BasePermission):
    """
    Allows access only to candidate users.
    """

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and User.CANDIDATE
        )
