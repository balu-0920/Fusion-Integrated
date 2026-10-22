from decimal import Decimal
from django.db.models import Q
from modules.elm.models import LeaveApplication, LeaveBalance, HolidayCalendar
from core.api.exceptions import ConflictError, BadRequestError,PermissionDeniedError

def calculate_leave_days(category: str, start_date, end_date, is_first_half, is_second_half) -> Decimal:
    """BR-EL-010 and BR-EL-011: Continuous counting vs working days."""
    if category == 'cl' and start_date == end_date and (is_first_half != is_second_half):
        return Decimal('0.5')
        
    days = (end_date - start_date).days + 1
    
    if category in ['el', 'col', 'vl']:
        return Decimal(str(days)) # Continuous counting
        
    # For CL, RH, SCL, exclude weekends and holidays
    holidays = set(HolidayCalendar.objects.filter(
        date__range=[start_date, end_date], is_restricted=False
    ).values_list('date', flat=True))
    
    actual_days = 0
    for i in range(days):
        current = start_date + timezone.timedelta(days=i)
        if current.weekday() < 5 and current not in holidays:
            actual_days += 1
            
    return Decimal(str(actual_days))

def check_overlap(applicant_id: int, start_date, end_date, is_first_half, is_second_half, exclude_id=None):
    """BR-EL-012: Overlap check with half-day exclusion logic."""
    qs = LeaveApplication.objects.filter(
        applicant_id=applicant_id,
        status__in=['approved', 'awaiting_unit_head', 'awaiting_establishment', 'awaiting_final_sanction']
    ).filter(start_date__lte=end_date, end_date__gte=start_date)
    
    if exclude_id:
        qs = qs.exclude(id=exclude_id)
        
    for app in qs:
        # If both are single half days on the exact same date, check if halves differ
        if app.start_date == start_date and app.end_date == end_date == start_date:
            if (app.is_first_half and is_second_half and not is_first_half) or \
               (app.is_second_half and is_first_half and not is_second_half):
                continue
        raise ConflictError("Leave period overlaps with an existing request.", code="overlap_detected")

def apply_for_leave(applicant_id: int, data: dict, is_director: bool = False):
    """EL-UC-001: Validate and submit new application."""
    days = calculate_leave_days(
        data['category'], data['start_date'], data['end_date'], 
        data.get('is_first_half', False), data.get('is_second_half', False)
    )
    
    check_overlap(applicant_id, data['start_date'], data['end_date'], 
                  data.get('is_first_half', False), data.get('is_second_half', False))
    
    if data.get('substitute_id'):
        if data['substitute_id'] == applicant_id:
            raise BadRequestError("Substitute cannot be the applicant.")
        check_overlap(data['substitute_id'], data['start_date'], data['end_date'], False, False)
        status = 'awaiting_substitute'
    else:
        status = 'awaiting_director_self_sanction' if is_director else 'awaiting_unit_head'
        
    app = LeaveApplication.objects.create(
        applicant_id=applicant_id,
        deducted_days=days,
        status=status,
        **data
    )
    return app

def withdraw_leave(application_id: int, actor_id: int):
    """EL-UC-007: Immediate withdrawal of pending request."""
    app = LeaveApplication.objects.get(id=application_id, applicant_id=actor_id)
    if app.status in ['approved', 'rejected', 'cancelled', 'withdrawn']:
        raise ConflictError("Cannot withdraw a finalized request.")
    
    app.status = 'withdrawn'
    app.save(update_fields=['status', 'updated_at'])
    return app


def handle_substitute_response(application_id: int, actor_id: int, action: str, is_director_applicant: bool):
    """EL-UC-002: Process substitute consent and route accordingly."""
    app = LeaveApplication.objects.get(id=application_id, status='awaiting_substitute')
    
    if app.substitute_id != actor_id:
        raise PermissionDeniedError("You are not the nominated substitute.")
        
    if action == 'accept':
        # BR-EL-020 & BW-EL-08: Director bypasses Unit Head
        app.status = 'awaiting_director_self_sanction' if is_director_applicant else 'awaiting_unit_head'
    elif action == 'decline':
        app.status = 'applicant_action_required'
        
    app.save(update_fields=['status', 'updated_at'])
    return app

def unit_head_review(application_id: int, actor_id: int, action: str, establishment_configured: bool):
    """EL-UC-003: Unit Head decision or recommendation."""
    app = LeaveApplication.objects.get(id=application_id, status='awaiting_unit_head')
    
    # BR-EL-016: Final decision for CL / RH
    if app.category in ['cl', 'rh']:
        if action not in ['approve', 'reject']:
            raise BadRequestError("Unit Head must approve or reject CL/RH.")
        app.status = 'approved' if action == 'approve' else 'rejected'
        
    # BR-EL-017: Recommendation for Higher Sanction (SCL, EL, COL, VL)
    else:
        if action not in ['recommend', 'not_recommend']:
            raise BadRequestError("Unit Head can only recommend/not recommend higher-sanction leaves.")
        
        # BR-EL-018: Route forward regardless of recommendation
        app.status = 'awaiting_establishment_routing' if establishment_configured else 'awaiting_final_sanction_decision'

    app.save(update_fields=['status', 'updated_at'])
    return app

def final_sanction_decision(application_id: int, actor_id: int, action: str):
    """EL-UC-005: Final competent authority decision."""
    app = LeaveApplication.objects.get(id=application_id, status__in=['awaiting_final_sanction_decision', 'awaiting_director_self_sanction'])
    
    if action not in ['approve', 'reject']:
        raise BadRequestError("Invalid sanctioning action.")
        
    app.status = 'approved' if action == 'approve' else 'rejected'
    
    # Note: In a full implementation, balance deduction logic (BR-EL-002 to BR-EL-009) 
    # would be executed here upon approval.
    
    app.save(update_fields=['status', 'updated_at'])
    return app

def request_cancellation(application_id: int, actor_id: int):
    """EL-UC-008: Request cancellation of approved leave before start."""
    app = LeaveApplication.objects.get(id=application_id, applicant_id=actor_id, status='approved')
    
    # BR-EL-023: Cancellation only valid before start date
    if timezone.now().date() >= app.start_date:
        raise BadRequestError("Leave has already started; use extension or resumption instead.")
    
    app.status = 'cancellation_pending_unit_head'
    app.save(update_fields=['status', 'updated_at'])
    return app

def review_resumption(application_id: int, actor_id: int):
    """EL-UC-011: Review resumption and determine sync requirements."""
    app = LeaveApplication.objects.get(id=application_id, status='resumption_review_pending')
    
    # BR-EL-028: Normal, Early, and Late Resumption Outcomes
    if app.actual_resumption_date == app.end_date:
        app.status = 'resumption_reviewed_no_adjustment'
    elif app.actual_resumption_date < app.end_date:
        app.status = 'resumption_reviewed_early_return'
        # TODO: Restore unused balance fraction
    else:
        app.status = 'resumption_reviewed_late_return'
        # TODO: Deduct additional balance fraction
        
    app.save(update_fields=['status', 'updated_at'])
    return app