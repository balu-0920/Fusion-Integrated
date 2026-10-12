from decimal import Decimal
from django.db.models import Q
from modules.elm.models import LeaveApplication, LeaveBalance, HolidayCalendar
from core.api.exceptions import ConflictError, BadRequestError

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