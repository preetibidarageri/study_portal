from rest_framework.permissions import BasePermission, SAFE_METHODS
from .models import UserProfile
class IsTeacherOrReadOnly(BasePermission):
    """
    Allow anyone with a valid login to view subjects.
    only teachers can create, subjects.
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return request.user and request.user.is_authenticated

        if not request.user or not request.user.is_authenticated:
            return False

        try:
            return request.user.profile.role == "teacher"
        except UserProfile.DoesNotExist:
            return False