import os

from celery import Celery
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")

app = Celery("fusion_integrated")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

# Each installed module contributes its own schedules and task routes.
app.conf.beat_schedule = {}
app.conf.task_routes = {}

if "modules.placement" in settings.INSTALLED_APPS:
    from modules.placement.schedule import (
        BEAT_SCHEDULE as PLACEMENT_SCHEDULE,
    )
    from modules.placement.schedule import (
        TASK_ROUTES as PLACEMENT_ROUTES,
    )

    app.conf.beat_schedule.update(PLACEMENT_SCHEDULE)
    app.conf.task_routes.update(PLACEMENT_ROUTES)
