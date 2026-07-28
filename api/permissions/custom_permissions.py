from rest_framework.permissions import BasePermission

class IsApprovedUser(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.role == 'CLIENT':
            if request.user.client and request.user.client.status != 'ACTIVE':
                return False
            return request.user.status == 'APPROVED'
        return True
