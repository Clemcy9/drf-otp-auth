from celery import shared_task
from apps.audit.tasks import create_audit_log

@shared_task
def send_otp_email(email, otp):
    # send email b4 logging
    print(f"[OTP Email] Sent to {email}: {otp}")
