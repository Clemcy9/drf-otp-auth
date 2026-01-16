from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema
from django.conf import settings
from django.contrib.auth import get_user_model
from .serializers import OTPRequestSerializer, OTPVerifySerializer, RegisterSerializer
from .services import OTPService
from .tasks import send_otp_email
from apps.audit.tasks import create_audit_log
from apps.audit.utils import get_request_meta

User = get_user_model()


class RegisterView(APIView):

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "User registered successfully"}, status=status.HTTP_201_CREATED)

class OTPRequestView(APIView):

    @extend_schema(
        request=OTPRequestSerializer,
        responses={202: dict},
        description="Request OTP for email authentication"
    )

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




class OTPVerifyView(APIView):

    @extend_schema(
        request=OTPVerifySerializer,
        responses={200: dict},
        description="Verify OTP and receive JWT tokens"
    )

    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        otp_input = serializer.validated_data['otp']
        meta = get_request_meta(request)

        # Check lockout (failed attempts)
        ok, retry = OTPService.check_failed_attempts(email)
        if not ok:
            create_audit_log.delay(event="OTP_LOCKED", email=email, request_meta=meta)
            return Response(
                {"detail": "Too many failed attempts, account locked", "unlock_in": retry},
                status=status.HTTP_423_LOCKED
            )

        # Validate OTP
        otp_stored = OTPService.get_otp(email)
        if otp_stored != otp_input:
            OTPService.increment_failed_attempts(email)
            create_audit_log.delay(event="OTP_FAILED", email=email, request_meta=meta)
            return Response(
                {"detail": "Invalid OTP"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # OTP correct: one-time use
        OTPService.delete_otp(email)
        OTPService.reset_failed_attempts(email)

        # Create or update user
        user, created = User.objects.get_or_create(email=email)
        if created:
            user.set_unusable_password()  # OTP-only login
            user.save()

        # Issue JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        # Audit success
        create_audit_log.delay(event="OTP_VERIFIED", email=email, request_meta=meta)

        return Response(
            {
                "access": access_token,
                "refresh": str(refresh),
                "detail": "OTP verified successfully",
            },
            status=status.HTTP_200_OK
        )