from lariv.mixins import (
    ListViewMixin,
    DetailViewMixin,
    PostFormViewMixin,
    DeleteViewMixin,
    LarivHtmxMixin,
    BaseView,
)
from lariv.registry import ViewRegistry, EnvironmentRegistry
from .models import Tally
from django.utils import timezone
from django.urls import reverse, reverse_lazy
from django.core.exceptions import PermissionDenied


@ViewRegistry.register("tally.TallyList")
class TallyList(ListViewMixin):
    model = Tally
    component = "tally.TallyTable"
    key = "tallies"

    def get_queryset(self):
        queryset = super().get_queryset()

        env = EnvironmentRegistry.get("tally")(self.request)
        session = env.get_field_values().get("session")
        if not session:
            from .utils import ensure_session_for_date

            session = ensure_session_for_date(timezone.now().date())

        if session:
            queryset = queryset.filter(date__gte=session.start, date__lte=session.end)

        if not (
            self.request.user.is_superuser
            or self.request.user.role in ["totschool_admin"]
        ):
            queryset = queryset.filter(user=self.request.user)
        return queryset


@ViewRegistry.register("tally.TallyDailyForm")
class TallyDailyForm(PostFormViewMixin):
    model = Tally
    component = "tally.TallyDailyForm"
    key = "tally"
    success_url = reverse_lazy("tally:default")

    def get_object(self, pk=None):
        try:
            return self.get_queryset().get(
                user=self.request.user, date=timezone.now().date()
            )
        except Tally.DoesNotExist:
            return None

    def validate(self, data, inputs, instance=None):
        cleaned_data, errors = super().validate(data, inputs, instance)
        cleaned_data["user_id"] = self.request.user.id
        cleaned_data["date"] = timezone.now().date()
        return cleaned_data, errors


@ViewRegistry.register("tally.TallyCreate")
class TallyCreate(PostFormViewMixin):
    model = Tally
    component = "tally.TallyCreateForm"
    key = "tally"
    success_url = reverse_lazy("tally:default")

    def dispatch(self, request, *args, **kwargs):
        if not (request.user.is_superuser or request.user.role in ["totschool_admin"]):
            raise PermissionDenied("Only administrators can perform this action.")
        return super().dispatch(request, *args, **kwargs)


@ViewRegistry.register("tally.TallyView")
class TallyView(DetailViewMixin):
    model = Tally
    component = "tally.TallyDetail"
    key = "tally"


@ViewRegistry.register("tally.TallyUpdate")
class TallyUpdate(PostFormViewMixin):
    model = Tally
    component = "tally.TallyUpdateForm"
    key = "tally"

    def dispatch(self, request, *args, **kwargs):
        if not (request.user.is_superuser or request.user.role in ["totschool_admin"]):
            raise PermissionDenied("Only administrators can edit tallies.")
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self, obj):
        return reverse("tally:detail", kwargs={"pk": obj.pk})


@ViewRegistry.register("tally.TallyDelete")
class TallyDelete(DeleteViewMixin):
    model = Tally
    component = "tally.TallyDeleteForm"
    key = "tally"
    success_url = reverse_lazy("tally:default")

    def dispatch(self, request, *args, **kwargs):
        if not (request.user.is_superuser or request.user.role in ["totschool_admin"]):
            raise PermissionDenied("Only administrators can delete tallies.")
        return super().dispatch(request, *args, **kwargs)


@ViewRegistry.register("tally.TallyDashboard")
class TallyDashboard(LarivHtmxMixin, BaseView):
    model = Tally
    component = "tally.TallyDashboard"
    key = "dashboard"

    def prepare_data(self, request, **kwargs):
        user_id = request.GET.get("user_id", None)
        if not (request.user.is_superuser or request.user.role in ["totschool_admin"]):
            user_id = request.user.id

        env = EnvironmentRegistry.get("tally")(request)
        session = env.get_field_values().get("session")
        if not session:
            from .utils import ensure_session_for_date

            session = ensure_session_for_date(timezone.now().date())

        totals = Tally.objects.get_dashboard_stats(user_id=user_id, session=session)

        whatsapp_report = None
        if user_id and not (
            request.user.is_superuser or request.user.role in ["totschool_admin"]
        ):
            whatsapp_report = Tally.objects.get_whatsapp_report_data(user_id=user_id)

        return {"dashboard": totals, "whatsapp_report": whatsapp_report}


@ViewRegistry.register("tally.TallyLeaderboard")
class TallyLeaderboard(LarivHtmxMixin, BaseView):
    model = Tally
    component = "tally.TallyLeaderboard"
    key = "leaderboards"

    def prepare_data(self, request, **kwargs):
        user_id = request.GET.get("user_id", None)
        if not user_id:
            user_id = request.user.id

        env = EnvironmentRegistry.get("tally")(request)
        session = env.get_field_values().get("session")
        if not session:
            from .utils import ensure_session_for_date

            session = ensure_session_for_date(timezone.now().date())

        leaderboards = Tally.objects.get_leaderboards(user_id=user_id, session=session)
        return {
            "leaderboards": leaderboards,
            "title": f"Leaderboard for {session.name}",
        }
