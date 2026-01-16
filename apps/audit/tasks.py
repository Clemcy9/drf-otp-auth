from celery import shared_task
from .models import AuditLog

@shared_task
def create_audit_log(event, email, ip, user_agent, metadata=None):
    AuditLog.objects.create(
        event=event,
        email=email,
        ip_address=ip,
        user_agent=user_agent,
        metadata=metadata or {}
    )
