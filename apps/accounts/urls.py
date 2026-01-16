from django.urls import path
from .views import OTPRequestView, OTPVerifyView, RegisterView, LoginView, PasswordResetView, ForgotPasswordView

urlpatterns = [
    path("auth/register", RegisterView.as_view(), name="register"),
    path("auth/login", LoginView.as_view(), name="login"),
    path("auth/forgot-password", ForgotPasswordView.as_view(), name="forgot_password"),
    path("auth/password-reset", PasswordResetView.as_view(), name="password_reset"),
    path("auth/otp/request", OTPRequestView.as_view(), name="otp_request"),
    path("auth/otp/verify", OTPVerifyView.as_view(), name="otp_verify"),
]
