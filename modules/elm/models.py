from django.db import models
from django.utils import timezone

class LeaveBalance(models.Model):
    """Tracks current leave entitlements and balances per user per year."""
    user_id = models.IntegerField(db_index=True)
    year = models.IntegerField(default=timezone.now().year)
    
    cl_balance = models.DecimalField(max_digits=4, decimal_places=1, default=8.0)
    rh_balance = models.IntegerField(default=2)
    scl_balance = models.IntegerField(default=15)
    el_balance = models.DecimalField(max_digits=5, decimal_places=1, default=0.0)
    col_balance = models.DecimalField(max_digits=5, decimal_places=1, default=0.0)
    vl_balance = models.IntegerField(default=0)

    class Meta:
        unique_together = ("user_id", "year")

class LeaveApplication(models.Model):
    """Core state machine for ELM workflows (CW-EL-01 to CW-EL-04)."""
    CATEGORY_CHOICES = [
        ('cl', 'Casual Leave'), ('rh', 'Restricted Holiday'),
        ('scl', 'Special Casual Leave'), ('el', 'Earned Leave'),
        ('col', 'Commuted Leave'), ('vl', 'Vacation Leave')
    ]
    
    applicant_id = models.IntegerField(db_index=True)
    substitute_id = models.IntegerField(null=True, blank=True)
    
    category = models.CharField(max_length=5, choices=CATEGORY_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    is_first_half = models.BooleanField(default=False)
    is_second_half = models.BooleanField(default=False)
    
    purpose = models.TextField()
    station_leave = models.BooleanField(default=False)
    
    status = models.CharField(max_length=50, default='draft')
    deducted_days = models.DecimalField(max_digits=5, decimal_places=1, default=0.0)
    
    # Resumption tracking (EL-UC-010)
    actual_resumption_date = models.DateField(null=True, blank=True)
    
    # Workflow assignments
    unit_head_id = models.IntegerField(null=True, blank=True)
    sanctioning_authority_id = models.IntegerField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class HolidayCalendar(models.Model):
    """Effective published holiday/RH calendar (BR-EL-031)."""
    date = models.DateField(unique=True)
    name = models.CharField(max_length=100)
    is_restricted = models.BooleanField(default=False)