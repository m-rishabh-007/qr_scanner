from django.conf import settings


def product_identity(request):
    return {
        "PRODUCT_NAME": settings.PRODUCT_NAME,
        "COMPANY_NAME": settings.COMPANY_NAME,
        "SUPPORT_EMAIL": settings.SUPPORT_EMAIL,
        "PRIVACY_EMAIL": settings.PRIVACY_EMAIL,
    }
