from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from fusion_auth.permissions import HasModuleGrant, HasPermission
from core.api.exceptions import NotFoundError
from modules.elm.models import LeaveApplication
from modules.elm.api import serializers as s
from modules.elm import services

MODULE = HasModuleGrant("elm")

class LeaveApplyView(APIView):
    """EL-UC-001: Apply for Leave"""
    permission_classes = [MODULE]
    
    def post(self, request):
        payload = s.LeaveApplicationSerializer(data=request.data)
        payload.is_valid(raise_exception=True)
        
        actor = getattr(request, "principal")
        is_director = actor.role == "director"
        
        app = services.apply_for_leave(actor.user_id, payload.validated_data, is_director)
        return Response(s.LeaveApplicationSerializer(app).data, status=status.HTTP_201_CREATED)

class SubstituteResponseView(APIView):
    """EL-UC-002: Respond to Substitute Request"""
    permission_classes = [MODULE]
    
    def post(self, request, pk):
        payload = s.LeaveActionSerializer(data=request.data)
        payload.is_valid(raise_exception=True)
        
        actor = getattr(request, "principal")
        
        # In a real scenario, we check if the applicant was a director via User/Profile lookup.
        # Hardcoding False here for the base integration, to be expanded based on directory lookup.
        is_director_applicant = False 
        
        app = services.handle_substitute_response(
            pk, actor.user_id, payload.validated_data['action'], is_director_applicant
        )
        return Response(s.LeaveApplicationSerializer(app).data)

class UnitHeadReviewView(APIView):
    """EL-UC-003: Review Leave-Related Request at Unit Head"""
    permission_classes = [MODULE, HasPermission("elm.review_unit_head")]
    
    def post(self, request, pk):
        payload = s.LeaveActionSerializer(data=request.data)
        payload.is_valid(raise_exception=True)
        
        actor = getattr(request, "principal")
        # Assume establishment step is bypassed for this demo implementation
        establishment_configured = False 
        
        app = services.unit_head_review(pk, actor.user_id, payload.validated_data['action'], establishment_configured)
        return Response(s.LeaveApplicationSerializer(app).data)

class FinalSanctionView(APIView):
    """EL-UC-005: Make Final Sanctioning Decision"""
    permission_classes = [MODULE, HasPermission("elm.sanction_leave")]
    
    def post(self, request, pk):
        payload = s.LeaveActionSerializer(data=request.data)
        payload.is_valid(raise_exception=True)
        
        actor = getattr(request, "principal")
        app = services.final_sanction_decision(pk, actor.user_id, payload.validated_data['action'])
        return Response(s.LeaveApplicationSerializer(app).data)

class LeaveWithdrawView(APIView):
    """EL-UC-007: Withdraw Pending Request"""
    permission_classes = [MODULE]
    
    def post(self, request, pk):
        actor_id = getattr(request, "principal").user_id 
        app = services.withdraw_leave(pk, actor_id)
        return Response(s.LeaveApplicationSerializer(app).data)



class LeaveCancelView(APIView):
    """EL-UC-008: Request Cancellation of Approved Leave"""
    permission_classes = [MODULE]
    
    def post(self, request, pk):
        actor = getattr(request, "principal")
        app = services.request_cancellation(pk, actor.user_id)
        return Response(s.LeaveApplicationSerializer(app).data)

class ResumptionReviewView(APIView):
    """EL-UC-011: Review Resumption"""
    permission_classes = [MODULE, HasPermission("elm.sanction_leave")]
    
    def post(self, request, pk):
        actor = getattr(request, "principal")
        app = services.review_resumption(pk, actor.user_id)
        return Response(s.LeaveApplicationSerializer(app).data)    


class LeaveHistoryView(APIView):
    """EL-UC-012: View Leave Balances and History"""
    permission_classes = [MODULE]
    
    def get(self, request):
        actor_id = getattr(request, "principal").user_id
        apps = LeaveApplication.objects.filter(applicant_id=actor_id).order_by('-created_at')
        return Response(s.LeaveApplicationSerializer(apps, many=True).data)

class PendingApprovalsView(APIView):
    """Fetch queue for Unit Head / Sanctioning Authority"""
    permission_classes = [MODULE]
    
    def get(self, request):
        # Base query for demonstration; role-scoping applies in production
        apps = LeaveApplication.objects.filter(
            status__in=['awaiting_unit_head', 'awaiting_final_sanction_decision']
        ).order_by('-created_at')
        return Response(s.LeaveApplicationSerializer(apps, many=True).data)    