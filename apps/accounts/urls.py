from django.urls import path
from .views import OTPRequestView

urlpatterns = [
    path("auth/otp/request", OTPRequestView.as_view(), name="otp_request"),
]
