from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from core.api.exceptions import NotFoundError
from modules.elm.models import LeaveApplication, LeaveBalance
from modules.elm.api import serializers as s
from modules.elm import services

class LeaveApplyView(APIView):
    """EL-UC-001: Apply for Leave"""
    def post(self, request):
        payload = s.LeaveApplicationSerializer(data=request.data)
        payload.is_valid(raise_exception=True)
        # Using placeholder actor resolution logic typical for Fusion
        actor_id = getattr(request, "principal").user_id 
        is_director = getattr(request, "principal", None).role == "director"
        
        app = services.apply_for_leave(actor_id, payload.validated_data, is_director)
        return Response(s.LeaveApplicationSerializer(app).data, status=status.HTTP_201_CREATED)

class SubstituteResponseView(APIView):
    """EL-UC-002: Respond to Substitute Request"""
    def post(self, request, pk):
        payload = s.LeaveActionSerializer(data=request.data)
        payload.is_valid(raise_exception=True)
        
        app = LeaveApplication.objects.filter(id=pk, status='awaiting_substitute').first()
        if not app:
            raise NotFoundError("Pending substitute request not found.")
            
        action = payload.validated_data['action']
        if action == 'accept':
            # Director bypass unit head (BW-EL-08)
            app.status = 'awaiting_unit_head'
        elif action == 'decline':
            app.status = 'applicant_action_required'
            
        app.save(update_fields=['status'])
        return Response(s.LeaveApplicationSerializer(app).data)

class LeaveWithdrawView(APIView):
    """EL-UC-007: Withdraw Pending Request"""
    def post(self, request, pk):
        actor_id = getattr(request, "principal").user_id 
        app = services.withdraw_leave(pk, actor_id)
        return Response(s.LeaveApplicationSerializer(app).data)

class LeaveResumptionView(APIView):
    """EL-UC-010: Submit Resumption of Duty"""
    def post(self, request, pk):
        payload = s.ResumptionSerializer(data=request.data)
        payload.is_valid(raise_exception=True)
        
        app = LeaveApplication.objects.get(id=pk, status='approved')
        app.actual_resumption_date = payload.validated_data['actual_resumption_date']
        app.status = 'resumption_review_pending'
        app.save()
        
        return Response(s.LeaveApplicationSerializer(app).data)