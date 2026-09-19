from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Department, Member


User = get_user_model()


class PeopleApiTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username="admin", password="Strong-pass-123!", role=User.Role.ADMIN
        )
        self.teacher = User.objects.create_user(
            username="teacher", password="Strong-pass-123!", role=User.Role.TEACHER_HR
        )
        self.member_user = User.objects.create_user(
            username="member", password="Strong-pass-123!", role=User.Role.MEMBER
        )
        self.department = Department.objects.create(name="Engineering")
        self.member = Member.objects.create(
            user=self.member_user, employee_id="EMP-001", department=self.department
        )

    def test_admin_can_create_department(self):
        self.client.force_authenticate(self.admin)

        response = self.client.post("/api/departments/", {"name": "People"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Department.objects.filter(name="People").exists())

    def test_non_admin_cannot_create_department(self):
        self.client.force_authenticate(self.teacher)

        response = self.client.post("/api/departments/", {"name": "People"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_member_only_sees_their_own_member_record(self):
        other_user = User.objects.create_user(
            username="other", password="Strong-pass-123!", role=User.Role.MEMBER
        )
        Member.objects.create(
            user=other_user, employee_id="EMP-002", department=self.department
        )
        self.client.force_authenticate(self.member_user)

        response = self.client.get("/api/members/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["employee_id"], "EMP-001")
