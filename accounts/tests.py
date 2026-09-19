from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase


User = get_user_model()


class AuthenticationTests(APITestCase):
    def test_register_and_login(self):
        register = self.client.post(
            "/api/auth/register/",
            {"username": "new-user", "email": "new@example.com", "password": "Strong-pass-123!"},
            format="json",
        )

        self.assertEqual(register.status_code, status.HTTP_201_CREATED)
        login = self.client.post(
            "/api/auth/login/",
            {"username": "new-user", "password": "Strong-pass-123!"},
            format="json",
        )

        self.assertEqual(login.status_code, status.HTTP_200_OK)
        self.assertIn("access", login.data)
        self.assertIn("refresh", login.data)

    def test_admin_can_update_a_user_role(self):
        admin = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="Strong-pass-123!"
        )
        member = User.objects.create_user(
            username="member", email="member@example.com", password="Strong-pass-123!"
        )
        self.client.force_authenticate(admin)

        response = self.client.patch(
            f"/api/users/{member.pk}/role/", {"role": User.Role.TEACHER_HR}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        member.refresh_from_db()
        self.assertEqual(member.role, User.Role.TEACHER_HR)

    def test_non_admin_cannot_update_a_user_role(self):
        user = User.objects.create_user(
            username="member", email="member@example.com", password="Strong-pass-123!"
        )
        target = User.objects.create_user(
            username="target", email="target@example.com", password="Strong-pass-123!"
        )
        self.client.force_authenticate(user)

        response = self.client.patch(
            f"/api/users/{target.pk}/role/", {"role": User.Role.ADMIN}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
