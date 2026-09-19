from django.shortcuts import render
import csv
from django.db.models import Count, Q
from django.http import HttpResponse
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from accounts.models import User
from accounts.permissions import IsStaffRole
from .filters import AttendanceFilter
from .models import Attendance
from .serializers import AttendanceSerializer, BulkMarkSerializer


def _csv_safe(value):
    value = str(value)
    return f"'{value}" if value.startswith(("=", "+", "-", "@")) else value


class AttendanceViewSet(ModelViewSet):
    serializer_class = AttendanceSerializer
    filterset_class = AttendanceFilter
    search_fields = ["member__employee_id", "member__user__username"]

    def get_queryset(self):
        qs = Attendance.objects.select_related("member__user", "member__department")
        u = self.request.user

        if u.role == User.Role.MEMBER:
            return qs.filter(member__user_id=u.id)

        if u.role in (User.Role.TEACHER_HR, User.Role.ADMIN):
            return qs

        return qs.none()

    def get_permissions(self):
        if self.action in ("list", "retrieve", "summary"):
            return [IsAuthenticated()]
        return [IsStaffRole()]

    def perform_create(self, serializer):
        serializer.save(marked_by=self.request.user)

    @action(detail=False, methods=["post"])
    def bulk(self, request):
        ser = BulkMarkSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        date = ser.validated_data["date"]
        created = updated = 0

        for r in ser.validated_data["records"]:
            _, was_created = Attendance.objects.update_or_create(
                member=r["member"], date=date,
                defaults={"status": r["status"], "marked_by": request.user},
            )
            if was_created:
                created += 1
            else:
                updated += 1

        return Response({"created": created, "updated": updated})

    @action(detail=False, methods=["get"])
    def summary(self, request):
        qs = self.filter_queryset(self.get_queryset())

        data = (
            qs.values("member", "member__employee_id", "member__user__username")
            .annotate(
                total=Count("id"),
                present=Count("id", filter=Q(status="present")),
                absent=Count("id", filter=Q(status="absent")),
                leave=Count("id", filter=Q(status="leave")),
            )
            .order_by("member__employee_id")
        )
        return Response(list(data))

    @action(detail=False, methods=["get"])
    def export(self, request):
        qs = self.filter_queryset(self.get_queryset())
        resp = HttpResponse(content_type="text/csv")
        resp["Content-Disposition"] = 'attachment; filename="attendance.csv"'
        w = csv.writer(resp)
        w.writerow(["Date", "Employee ID", "Name", "Status"])
        for a in qs:
            w.writerow(
                [
                    _csv_safe(a.date),
                    _csv_safe(a.member.employee_id),
                    _csv_safe(a.member.user.username),
                    _csv_safe(a.status),
                ]
            )
        return resp
