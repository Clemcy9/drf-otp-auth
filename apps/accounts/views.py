from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import OTPRequestSerializer
from .services import OTPService
from .tasks import send_otp_email
from apps.audit.tasks import create_audit_log
from apps.audit.utils import get_request_meta


class OTPRequestView(APIView):

    def post(self, request):
        serializer = OTPRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        ip = request.META.get('REMOTE_ADDR', '')
        
        # Rate limiting
        ok, retry = OTPService.check_email_rate_limit(email)
        if not ok:
            return Response(
                {"detail": "Too many requests for this email", "retry_after": retry},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )

        ok, retry = OTPService.check_ip_rate_limit(ip)
        if not ok:
            return Response(
                {"detail": "Too many requests from this IP", "retry_after": retry},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )

        # Generate OTP
        otp = OTPService.generate_otp()
        OTPService.store_otp(email, otp)

        # Increment counters
        OTPService.increment_email_counter(email)
        OTPService.increment_ip_counter(ip)

        # Async tasks
        send_otp_email.delay(email, otp)
        meta = get_request_meta(request)
        create_audit_log.delay(event="OTP_REQUESTED", email=email, request_meta=meta)

        return Response(
            {"detail": "OTP sent", "expires_in": 300},
            status=status.HTTP_202_ACCEPTED
        )
