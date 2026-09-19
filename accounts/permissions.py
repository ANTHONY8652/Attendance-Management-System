from rest_framework.permissions import BasePermission
from .models import User

class IsAdminRole(BasePermission):
    def has_permission(self, request, view):
        u = request.user
        return bool(u and u.is_authenticated and u.role == User.Role.ADMIN)

class IsStaffRole(BasePermission):
    def has_permission(self, request, view):
        u = request.user
        return bool(
            u
            and u.is_authenticated
            and u.role in (User.Role.TEACHER_HR, User.Role.ADMIN)
        )