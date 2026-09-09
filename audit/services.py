from audit.models import AuditLog


class AuditLogService:

    @staticmethod
    def get_ip_address(request):
        return request.META.get("REMOTE_ADDR")

    @staticmethod
    def log(
        *,
        user=None,
        action,
        resource_type,
        resource_id=None,
        ip_address=None,
        details=None,
    ):
        return AuditLog.objects.create(
            user=user,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            details=details or {},
        )
