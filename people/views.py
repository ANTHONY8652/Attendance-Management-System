from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from accounts.models import User
from accounts.permissions import IsAdminRole, IsStaffRole
from .models import Department, Member
from .serializers import MemberSerializer, DepartmentSerializer

class DepartmentViewSet(ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAdminRole]

class MemberViewSet(ModelViewSet):
    serializer_class = MemberSerializer
    filterset_fields = ["department"]
    search_fields = ["employee_id", "user__username", "user__first_name", "user__last_name"]
    
    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [IsAuthenticated()]
        return [IsStaffRole()]
    
    def get_queryset(self):
        qs = Member.objects.select_related("user", "department")
        u = self.request.user

        if u.role == User.Role.MEMBER:
            return qs.filter(user_id=u.id)

        if u.role in (User.Role.TEACHER_HR, User.Role.ADMIN):
            return qs

        return qs.none()
