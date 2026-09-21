from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'admin')


class IsStaffOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role in ('admin', 'staff')
        )


class IsOwnerOrStaff(BasePermission):
    """Client can access only their own objects; staff/admin see everything."""

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.role in ('admin', 'staff'):
            return True
        owner = getattr(obj, 'client', None)
        return owner_id_matches(owner, user)


def owner_id_matches(owner, user):
    return owner is not None and owner.id == user.id


class ReadOnlyOrStaff(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return bool(request.user and request.user.is_authenticated)
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role in ('admin', 'staff')
        )
