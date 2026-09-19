from datetime import date, timedelta

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from people.models import Department, Member

from .models import Attendance


User = get_user_model()


class AttendanceApiTests(APITestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(
            username="teacher", password="Strong-pass-123!", role=User.Role.TEACHER_HR
        )
        self.member_user = User.objects.create_user(
            username="member", password="Strong-pass-123!", role=User.Role.MEMBER
        )
        department = Department.objects.create(name="Engineering")
        self.member = Member.objects.create(
            user=self.member_user, employee_id="EMP-001", department=department
        )
        self.client.force_authenticate(self.teacher)

    def test_staff_can_create_attendance_and_list_it(self):
        response = self.client.post(
            "/api/attendance/",
            {"member": self.member.pk, "date": "2026-09-19", "status": "present"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["member_name"], "member")
        self.assertEqual(Attendance.objects.count(), 1)

        listing = self.client.get("/api/attendance/?status=present")
        self.assertEqual(listing.status_code, status.HTTP_200_OK)
        self.assertEqual(len(listing.data), 1)

    def test_duplicate_member_date_is_rejected(self):
        Attendance.objects.create(
            member=self.member, date=date(2026, 9, 19), status=Attendance.Status.PRESENT
        )

        response = self.client.post(
            "/api/attendance/",
            {"member": self.member.pk, "date": "2026-09-19", "status": "absent"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_bulk_marks_attendance_and_summary_counts_statuses(self):
        response = self.client.post(
            "/api/attendance/bulk/",
            {
                "date": "2026-09-19",
                "records": [{"member": self.member.pk, "status": "present"}],
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"created": 1, "updated": 0})
        summary = self.client.get("/api/attendance/summary/")
        self.assertEqual(summary.status_code, status.HTTP_200_OK)
        self.assertEqual(summary.data[0]["present"], 1)

    def test_future_date_is_rejected_by_bulk_endpoint(self):
        response = self.client.post(
            "/api/attendance/bulk/",
            {
                "date": (date.today() + timedelta(days=1)).isoformat(),
                "records": [{"member": self.member.pk, "status": "present"}],
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_member_only_sees_their_own_attendance(self):
        Attendance.objects.create(
            member=self.member, date=date(2026, 9, 19), status=Attendance.Status.PRESENT
        )
        self.client.force_authenticate(self.member_user)

        response = self.client.get("/api/attendance/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
