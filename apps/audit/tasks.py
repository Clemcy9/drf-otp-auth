from celery import shared_task
from .models import AuditLog


@shared_task
def create_audit_log(event, email, request_meta=None, metadata=None):
    ip = None
    user_agent = None

    if request_meta:
        ip = request_meta.get("ip")
        user_agent = request_meta.get("user_agent")

    AuditLog.objects.create(
        event=event,
        email=email,
        ip_address=ip,
        user_agent=user_agent,
        metadata=metadata or {}
    )