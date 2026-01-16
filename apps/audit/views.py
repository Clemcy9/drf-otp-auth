from django.shortcuts import render

# Create your views here.
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema

from .models import AuditLog
from .serializers import AuditLogSerializer
from .filters import AuditLogFilter
from .pagination import AuditPagination

class AuditLogListView(ListAPIView):

    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = AuditPagination
    filterset_class = AuditLogFilter

    @extend_schema(
        description="Get audit logs (JWT protected). "
                    "Filters: email, event, from_date, to_date"
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
