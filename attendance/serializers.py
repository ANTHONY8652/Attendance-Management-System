from django.utils import timezone
from rest_framework import serializers
from people.models import Member
from .models import Attendance
from rest_framework.validators import UniqueTogetherValidator

class AttendanceSerializer(serializers.ModelSerializer):
    member_name = serializers.CharField(source="member.user.username", read_only=True)
    
    class Meta:
        validators = [
            UniqueTogetherValidator(
                queryset=Attendance.objects.all(),
                fields=["member", "date"],
                message="Already marked for this day.",
            )
        ]
        model = Attendance
        fields = ["id", "member", "member_name", "date", "status", "marked_by", "created_at", "updated_at"]
        read_only_fields = ["marked_by", "created_at", "updated_at"]
    
class BulkItemSerializer(serializers.Serializer):
    member = serializers.PrimaryKeyRelatedField(queryset=Member.objects.all())
    status = serializers.ChoiceField(choices=Attendance.Status.choices)

class BulkMarkSerializer(serializers.Serializer):
    date = serializers.DateField()
    records = BulkItemSerializer(many=True, allow_empty=False)
    
    def validate_date(self, value):
        if value > timezone.localdate():
            raise serializers.ValidationError("Can't mark future dates sorry try another date instead.")
        
        return value