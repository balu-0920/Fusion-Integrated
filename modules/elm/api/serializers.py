from rest_framework import serializers
from modules.elm.models import LeaveApplication, LeaveBalance

class LeaveBalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveBalance
        exclude = ('id',)

class LeaveApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveApplication
        fields = '__all__'
        read_only_fields = ('status', 'deducted_days', 'actual_resumption_date', 'created_at', 'updated_at')

class LeaveActionSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=['approve', 'reject', 'recommend', 'not_recommend', 'accept', 'decline'])
    remarks = serializers.CharField(max_length=300, required=False, allow_blank=True)

class ResumptionSerializer(serializers.Serializer):
    actual_resumption_date = serializers.DateField()