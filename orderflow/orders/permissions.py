from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsOwnerOrHasOrderPerms(BasePermission):
    """
    Object-level RBAC:
      - SAFE methods pass (queryset already scoped in selectors).
      - PUT/PATCH: owner OR 'orders.edit_any_order'.
      - DELETE:     owner OR 'orders.delete_any_order'.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        is_owner = getattr(obj, "is_owner", None)
        is_owner = is_owner(request.user) if callable(is_owner) else False

        if request.method in ("PUT", "PATCH"):
            return is_owner or request.user.has_perm("orders.edit_any_order")
        if request.method == "DELETE":
            return is_owner or request.user.has_perm("orders.delete_any_order")
        return False
