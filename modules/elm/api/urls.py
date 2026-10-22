from django.urls import path
from modules.elm.api import views as v

urlpatterns = [
    path("applications/apply", v.LeaveApplyView.as_view(), name="elm-apply"),
    path("applications/<int:pk>/substitute", v.SubstituteResponseView.as_view(), name="elm-substitute"),
    path("applications/<int:pk>/unit-head-review", v.UnitHeadReviewView.as_view(), name="elm-unit-head-review"),
    path("applications/<int:pk>/sanction", v.FinalSanctionView.as_view(), name="elm-sanction"),
    path("applications/<int:pk>/withdraw", v.LeaveWithdrawView.as_view(), name="elm-withdraw"),
    # Append these below the existing elm-resume route:
    path("applications/<int:pk>/cancel", v.LeaveCancelView.as_view(), name="elm-cancel"),
    path("applications/<int:pk>/resumption-review", v.ResumptionReviewView.as_view(), name="elm-resumption-review"),
    # path("applications/<int:pk>/resume", v.LeaveResumptionView.as_view(), name="elm-resume"),
]