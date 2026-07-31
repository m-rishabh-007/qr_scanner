from rest_framework.permissions import BasePermission

from apps.accounts.models import MerchantAccount


class IsApprovedMerchant(BasePermission):
    def has_permission(self, request, view):
        account = getattr(request.user, "merchant_account", None)
        return bool(
            request.user.is_authenticated
            and account
            and account.status == MerchantAccount.Status.APPROVED
        )
