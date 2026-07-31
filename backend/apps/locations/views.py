from io import BytesIO

import qrcode
from django.conf import settings
from django.http import HttpResponse
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.catalog.models import Domain

from .models import Location, qr_token
from .permissions import IsApprovedMerchant
from .serializers import DomainOptionSerializer, LocationSerializer
from .validators import validate_google_review_url


class DomainOptionsView(APIView):
    permission_classes = [IsApprovedMerchant]

    def get(self, request):
        return Response(DomainOptionSerializer(Domain.objects.filter(active=True), many=True).data)


class MerchantLocationView(APIView):
    permission_classes = [IsApprovedMerchant]

    def get_object(self, request):
        return Location.objects.filter(merchant_account=request.user.merchant_account).first()

    def get(self, request):
        location = self.get_object(request)
        if not location:
            return Response(None)
        return Response(LocationSerializer(location, context={"request": request}).data)

    def post(self, request):
        if self.get_object(request):
            return Response({"detail": "MVP allows one location per merchant."}, status=409)
        serializer = LocationSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        location = serializer.save(merchant_account=request.user.merchant_account)
        return Response(LocationSerializer(location, context={"request": request}).data, status=201)

    def patch(self, request):
        location = self.get_object(request)
        if not location:
            return Response({"detail": "Location not found."}, status=404)
        serializer = LocationSerializer(
            location, data=request.data, partial=True, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class VerifyGoogleLinkView(APIView):
    permission_classes = [IsApprovedMerchant]

    def post(self, request):
        location = Location.objects.filter(merchant_account=request.user.merchant_account).first()
        if not location:
            return Response({"detail": "Location not found."}, status=404)
        validate_google_review_url(location.google_review_url)
        location.google_link_verified_at = timezone.now()
        location.save(update_fields=["google_link_verified_at"])
        return Response({"detail": "Link format verified. Merchant must still test the exact listing."})


class QrPngView(APIView):
    permission_classes = [IsApprovedMerchant]

    def get(self, request):
        location = Location.objects.filter(merchant_account=request.user.merchant_account).first()
        if not location:
            return Response({"detail": "Location not found."}, status=404)
        public_url = f"{settings.PUBLIC_BASE_URL}/r/{location.public_qr_token}/"
        image = qrcode.make(public_url)
        output = BytesIO()
        image.save(output, format="PNG")
        response = HttpResponse(output.getvalue(), content_type="image/png")
        response["Content-Disposition"] = f'inline; filename="{location.public_qr_token}.png"'
        return response


class RotateQrTokenView(APIView):
    permission_classes = [IsApprovedMerchant]

    def post(self, request):
        if request.data.get("confirmation") != "ROTATE":
            return Response({"detail": "Type ROTATE to confirm. Printed QR codes will stop working."}, status=400)
        location = Location.objects.filter(merchant_account=request.user.merchant_account).first()
        if not location:
            return Response({"detail": "Location not found."}, status=404)
        location.public_qr_token = qr_token()
        location.save(update_fields=["public_qr_token", "updated_at"])
        return Response(LocationSerializer(location, context={"request": request}).data)
