import httpx
from django.conf import settings
from django.db import connection
from django.http import JsonResponse


def health(request):
    return JsonResponse({"status": "ok"})


def readiness(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except Exception:
        return JsonResponse({"status": "unready", "database": "unavailable"}, status=503)
    return JsonResponse({"status": "ready", "database": "ok"})


def model_health(request):
    try:
        response = httpx.get(
            f"{settings.LITELLM_BASE_URL.rsplit('/v1', 1)[0]}/health/liveliness",
            headers={"Authorization": f"Bearer {settings.LITELLM_API_KEY}"},
            timeout=3,
        )
        response.raise_for_status()
    except Exception:
        return JsonResponse({"status": "degraded", "model_gateway": "unavailable"}, status=503)
    return JsonResponse({"status": "ok", "model_gateway": "available"})
