"""Umumiy DRF ruxsat sinflari."""

from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdminOrReadOnly(BasePermission):
    """O'qish hammaga ochiq, o'zgartirish faqat xodimlar uchun."""

    def has_permission(self, request, view) -> bool:
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)


class IsOwner(BasePermission):
    """Obyekt faqat egasiga ochiq."""

    owner_field = "user"

    def has_object_permission(self, request, view, obj) -> bool:
        owner = getattr(obj, getattr(view, "owner_field", self.owner_field), None)
        return owner is not None and owner == request.user
