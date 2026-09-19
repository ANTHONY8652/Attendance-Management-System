from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import User
from .permissions import IsAdminRole
from .serializers import RegisterSerializer, RoleUpdateSerializer

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    
class SetRoleView(APIView):
    permission_classes = [IsAdminRole]

    def patch(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        serializer = RoleUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user.role = serializer.validated_data["role"]
        user.save(update_fields=["role"])
        return Response({"id": user.id, "role": user.role})

# Create your views here.
