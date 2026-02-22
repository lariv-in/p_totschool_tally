from django.db.models import Sum, Count, Value, IntegerField
from django.db.models.functions import Coalesce
from lariv.mixins import (
    ListViewMixin,
    DetailViewMixin,
    PostFormViewMixin,
    DeleteViewMixin,
    LarivHtmxMixin,
    BaseView,
)
from lariv.registry import ViewRegistry
from .models import Tally


@ViewRegistry.register("tally.TallyList")
class TallyList(ListViewMixin):
    model = Tally
    component = "tally.TallyTable"
    key = "tallies"


@ViewRegistry.register("tally.TallyCreate")
class TallyCreate(PostFormViewMixin):
    model = Tally
    component = "tally.TallyCreateForm"
    key = "tally"
    success_url_name = "tally:default"


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
    success_url_name = "tally:detail"


@ViewRegistry.register("tally.TallyDelete")
class TallyDelete(DeleteViewMixin):
    model = Tally
    component = "tally.TallyDeleteForm"
    key = "tally"
    success_url_name = "tally:default"


@ViewRegistry.register("tally.TallyDashboard")
class TallyDashboard(LarivHtmxMixin, BaseView):
    model = Tally
    component = "tally.TallyDashboard"
    key = "dashboard"

    def prepare_data(self, request, **kwargs):
        user_id = request.GET.get("user_id", None)

        queryset = Tally.objects.all()
        if user_id:
            queryset = queryset.filter(user=user_id)

        totals = queryset.aggregate(
            total_calls=Coalesce(Sum("calls"), Value(0), output_field=IntegerField()),
            total_leads=Coalesce(Sum("leads"), Value(0), output_field=IntegerField()),
            total_visits=Coalesce(Sum("visits"), Value(0), output_field=IntegerField()),
            total_appointments=Coalesce(
                Sum("appointments"), Value(0), output_field=IntegerField()
            ),
            total_demos=Coalesce(Sum("demos"), Value(0), output_field=IntegerField()),
            total_letters=Coalesce(
                Sum("letters"), Value(0), output_field=IntegerField()
            ),
            total_follow_ups=Coalesce(
                Sum("follow_ups"), Value(0), output_field=IntegerField()
            ),
            total_proposals=Coalesce(
                Sum("proposals"), Value(0), output_field=IntegerField()
            ),
            total_policies=Coalesce(
                Sum("policies"), Value(0), output_field=IntegerField()
            ),
            total_premium=Coalesce(
                Sum("premium"), Value(0), output_field=IntegerField()
            ),
            forms_filled=Count("id"),
        )

        # Calculate conversion rates with new ratios
        appt_visit_ratio = 0
        demo_appt_ratio = 0
        policy_demo_ratio = 0

        if totals["total_visits"] > 0:
            appt_visit_ratio = round(
                (totals["total_appointments"] / totals["total_visits"]) * 100, 1
            )
        if totals["total_appointments"] > 0:
            demo_appt_ratio = round(
                (totals["total_demos"] / totals["total_appointments"]) * 100, 1
            )
        if totals["total_demos"] > 0:
            policy_demo_ratio = round(
                (totals["total_policies"] / totals["total_demos"]) * 100, 1
            )

        totals["appt_visit_ratio"] = appt_visit_ratio
        totals["demo_appt_ratio"] = demo_appt_ratio
        totals["policy_demo_ratio"] = policy_demo_ratio

        return {"dashboard": totals}
