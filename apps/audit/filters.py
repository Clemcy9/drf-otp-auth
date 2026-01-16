import django_filters
from .models import AuditLog

class AuditLogFilter(django_filters.FilterSet):

    email = django_filters.CharFilter(field_name="email", lookup_expr="iexact")
    event = django_filters.CharFilter(field_name="event", lookup_expr="iexact")
    from_date = django_filters.DateTimeFilter(
        field_name="created_at", lookup_expr="gte"
    )
    to_date = django_filters.DateTimeFilter(
        field_name="created_at", lookup_expr="lte"
    )

    class Meta:
        model = AuditLog
        fields = ["email", "event", "from_date", "to_date"]
