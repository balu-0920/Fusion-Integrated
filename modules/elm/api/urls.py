from django.urls import path
from modules.elm.api import views as v

urlpatterns = [
    path("applications/apply", v.LeaveApplyView.as_view(), name="elm-apply"),
    path("applications/<int:pk>/substitute", v.SubstituteResponseView.as_view(), name="elm-substitute"),
    path("applications/<int:pk>/withdraw", v.LeaveWithdrawView.as_view(), name="elm-withdraw"),
    path("applications/<int:pk>/resume", v.LeaveResumptionView.as_view(), name="elm-resume"),
]