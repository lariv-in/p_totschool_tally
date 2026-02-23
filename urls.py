from django.urls import path
from lariv.registry import ViewRegistry
from . import views  # noqa: F401

TallyList = ViewRegistry.get("tally.TallyList")
TallyDailyForm = ViewRegistry.get("tally.TallyDailyForm")
TallyCreate = ViewRegistry.get("tally.TallyCreate")
TallyView = ViewRegistry.get("tally.TallyView")
TallyUpdate = ViewRegistry.get("tally.TallyUpdate")
TallyDelete = ViewRegistry.get("tally.TallyDelete")
TallyDashboard = ViewRegistry.get("tally.TallyDashboard")

TallyLeaderboard = ViewRegistry.get("tally.TallyLeaderboard")

app_name = "tally"

urlpatterns = [
    path("", TallyDashboard.as_view(), name="default"),
    path("list/", TallyList.as_view(), name="list"),
    path("dashboard/", TallyDashboard.as_view(), name="dashboard"),
    path("leaderboard/", TallyLeaderboard.as_view(), name="leaderboard"),
    path("daily/", TallyDailyForm.as_view(), name="daily"),
    path("create/", TallyCreate.as_view(), name="create"),
    path("<int:pk>/", TallyView.as_view(), name="detail"),
    path("<int:pk>/update/", TallyUpdate.as_view(), name="update"),
    path("<int:pk>/delete/", TallyDelete.as_view(), name="delete"),
]
