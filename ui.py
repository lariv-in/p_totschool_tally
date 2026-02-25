from django.urls import reverse_lazy, reverse
from lariv.registry import UIRegistry, EnvironmentRegistry
from lariv.environment import Environment as LarivEnvironment, EnvironmentField
from users.models import User
from django.utils import timezone
from .models import TotSchoolSession
from components import *  # noqa
from components.base import Component
from .components.tally_components import *  # noqa


@EnvironmentRegistry.register("tally")
class TallyEnvironment(LarivEnvironment):
    """Environment configuration for the Tally app."""

    redirect_url = reverse_lazy("tally:default")

    session = EnvironmentField(
        model=TotSchoolSession,
        session_key="session",
        label="Session",
    )

    def get_field_values(self):
        values = super().get_field_values()
        if not values.get("session"):
            from .utils import ensure_session_for_date

            values["session"] = ensure_session_for_date(timezone.now().date())
        return values

    def get_field_data(self):
        data = super().get_field_data()
        for field in data:
            if field["name"] == "session" and not field["value"]:
                from .utils import ensure_session_for_date

                field["value"] = ensure_session_for_date(timezone.now().date())
        return data


# Menus
@UIRegistry.register("tally.TallyMenu")
class TallyMenu(Component):
    def build(self):
        return Menu(
            uid="tally-menu",
            title="Tally",
            back=MenuItem(
                uid="tally-menu-back",
                title="Back to All Apps",
                url=reverse_lazy("apps"),
            ),
            children=[
                MenuItem(
                    uid="tally-menu-dashboard",
                    title="Dashboard",
                    url=reverse_lazy("tally:dashboard"),
                ),
                MenuItem(
                    uid="tally-menu-leaderboard",
                    title="Leaderboard",
                    url=reverse_lazy("tally:leaderboard"),
                ),
                MenuItem(
                    uid="tally-menu-list",
                    title="All Reports",
                    url=reverse_lazy("tally:list"),
                ),
                MenuItem(
                    uid="tally-menu-daily",
                    title="Fill Daily Report",
                    url=reverse_lazy("tally:daily"),
                ),
                MenuItem(
                    uid="tally-menu-create",
                    title="Create Tally (Admin)",
                    role=["totschool_admin"],
                    url=reverse_lazy("tally:create"),
                ),
            ],
        )


@UIRegistry.register("tally.TallyDetailMenu")
class TallyDetailMenu(Component):
    def build(self):
        return Menu(
            uid="tally-detail-menu",
            back=MenuItem(
                uid="tally-detail-menu-back",
                title="Back to all Tallies",
                url=reverse_lazy("tally:default"),
            ),
            key="tally",
            title=lambda o: f"Tally: {o.user.name} ({o.date})",
            children=[
                MenuItem(
                    uid="tally-detail-menu-detail",
                    title="Tally Detail",
                    key="tally",
                    url=lambda o: reverse("tally:detail", args=[o.pk]),
                ),
                MenuItem(
                    uid="tally-detail-menu-edit",
                    title="Edit Tally",
                    key="tally",
                    url=lambda o: reverse("tally:update", args=[o.pk]),
                ),
                MenuItem(
                    uid="tally-detail-menu-delete",
                    title="Delete Tally",
                    key="tally",
                    url=lambda o: reverse("tally:delete", args=[o.pk]),
                ),
            ],
        )


# Filters for Tally
@UIRegistry.register("tally.TallyFilter")
class TallyFilter(Component):
    def build(self):
        return Form(
            uid="tally-filter",
            action=reverse_lazy("tally:list"),
            target="#tally-table_display_content",
            method="get",
            swap="morph",
            children=[
                ForeignKeyInput(
                    uid="tally-filter-user",
                    key="user",
                    label="User",
                    model=User,
                    selection_url=reverse_lazy("users:select"),
                    placeholder="Select User",
                ),
                DateInput(uid="tally-filter-date", key="date", label="Date"),
                Row(
                    uid="tally-filter-actions",
                    classes="flex gap-2",
                    children=[
                        SubmitInput(
                            uid="tally-filter-submit",
                            label="Apply",
                        ),
                        ClearInput(uid="tally-filter-clear", label="Clear"),
                    ],
                ),
            ],
        )


# Forms for Tally
class DynamicDate:
    def __str__(self):
        return timezone.now().date().strftime("%b %d, %Y")


def get_tally_common_fields(prefix):
    return [
        Row(
            uid=f"{prefix}-visits-appts",
            classes="grid grid-cols-1 gap-1 @md:grid-cols-2",
            children=[
                TextInput(
                    uid=f"{prefix}-visits", key="visits", label="Visits", required=True
                ),
                TextInput(
                    uid=f"{prefix}-appointments",
                    key="appointments",
                    label="Appointments",
                    required=True,
                ),
            ],
        ),
        Row(
            uid=f"{prefix}-leads-calls",
            classes="grid grid-cols-1 gap-1 @md:grid-cols-2",
            children=[
                TextInput(
                    uid=f"{prefix}-leads", key="leads", label="Leads", required=True
                ),
                TextInput(
                    uid=f"{prefix}-calls",
                    key="calls",
                    label="Calls",
                    required=True,
                ),
            ],
        ),
        Row(
            uid=f"{prefix}-demos-letters",
            classes="grid grid-cols-1 gap-1 @md:grid-cols-2",
            children=[
                TextInput(
                    uid=f"{prefix}-demos",
                    key="demos",
                    label="Demonstrations",
                    required=True,
                ),
                TextInput(
                    uid=f"{prefix}-letters",
                    key="letters",
                    label="Follow Up Letters Sent",
                    required=True,
                ),
            ],
        ),
        Row(
            uid=f"{prefix}-followups-proposals",
            classes="grid grid-cols-1 gap-1 @md:grid-cols-2",
            children=[
                TextInput(
                    uid=f"{prefix}-followups",
                    key="follow_ups",
                    label="Follow Ups",
                    required=True,
                ),
                TextInput(
                    uid=f"{prefix}-proposals",
                    key="proposals",
                    label="Proposals Given",
                    required=True,
                ),
            ],
        ),
        Row(
            uid=f"{prefix}-policies-premium",
            classes="grid grid-cols-1 gap-1 @md:grid-cols-2",
            children=[
                TextInput(
                    uid=f"{prefix}-policies",
                    key="policies",
                    label="Policies Sold",
                    required=True,
                ),
                TextInput(
                    uid=f"{prefix}-premium",
                    key="premium",
                    label="Premium",
                    required=True,
                ),
            ],
        ),
    ]


@UIRegistry.register("tally.TallyFormFields")
class TallyFormFields(Component):
    def build(self):
        return Column(
            uid="tally-form-fields",
            children=[
                Row(
                    uid="tally-form-user-row",
                    classes="grid grid-cols-1 gap-1 @md:grid-cols-2",
                    children=[
                        ForeignKeyInput(
                            uid="tally-form-user",
                            key="user",
                            label="Agent",
                            selection_url=reverse_lazy("users:select"),
                            display_attr="name",
                            placeholder="Select Agent",
                            required=True,
                            model=User,
                        ),
                        DateInput(
                            uid="tally-form-date",
                            key="date",
                            label="Date",
                            required=True,
                        ),
                    ],
                ),
                *get_tally_common_fields("tally-form"),
                SubmitInput(uid="tally-form-submit", label="Save"),
            ],
        )


@UIRegistry.register("tally.TallyCreateForm")
class TallyCreateForm(Component):
    def build(self):
        return ScaffoldLayout(
            uid="tally-create-scaffold",
            sidebar_children=[UIRegistry.get("tally.TallyMenu")().build()],
            children=[
                Form(
                    uid="tally-create-form",
                    action=reverse_lazy("tally:create"),
                    target="#app-layout",
                    key="tally",
                    title="Create Tally",
                    subtitle="Log Daily Performance",
                    classes="@container",
                    children=[UIRegistry.get("tally.TallyFormFields")().build()],
                )
            ],
        )


@UIRegistry.register("tally.TallyUpdateForm")
class TallyUpdateForm(Component):
    def build(self):
        return ScaffoldLayout(
            uid="tally-update-scaffold",
            sidebar_children=[UIRegistry.get("tally.TallyDetailMenu")().build()],
            children=[
                Form(
                    uid="tally-update-form",
                    action=lambda obj: reverse("tally:update", args=[obj.pk]),
                    target="#app-layout",
                    key="tally",
                    title="Edit Tally Form",
                    subtitle="Update Daily Performance",
                    classes="@container",
                    children=[UIRegistry.get("tally.TallyFormFields")().build()],
                )
            ],
        )


@UIRegistry.register("tally.TallyDailyForm")
class TallyDailyForm(Component):
    def build(self):
        return ScaffoldLayout(
            uid="tally-daily-scaffold",
            sidebar_children=[UIRegistry.get("tally.TallyMenu")().build()],
            children=[
                Form(
                    uid="tally-daily-form",
                    action=lambda obj: reverse("tally:daily"),
                    target="#app-layout",
                    key="tally",
                    title="Daily Report",
                    subtitle=DynamicDate(),
                    classes="@container",
                    children=[
                        *get_tally_common_fields("tally-daily-form"),
                        SubmitInput(uid="tally-daily-form-submit", label="Save"),
                    ],
                ),
            ],
        )


# Tally Table
@UIRegistry.register("tally.TallyTable")
class TallyTable(Component):
    def build(self):
        return ScaffoldLayout(
            uid="tally-table-scaffold",
            sidebar_children=[UIRegistry.get("tally.TallyMenu")().build()],
            children=[
                Table(
                    uid="tally-table",
                    classes="w-full",
                    key="tallies",
                    title="Tallies",
                    subtitle="All Daily Reports",
                    row_url=lambda o: reverse("tally:detail", args=[o.pk]),
                    filter_component=UIRegistry.get("tally.TallyFilter")().build(),
                    columns=[
                        TableColumn(
                            uid="tally-col-user",
                            label="Agent",
                            key="user",
                            component=TextField(uid="tally-col-user-field", key="user"),
                        ),
                        TableColumn(
                            uid="tally-col-date",
                            label="Date",
                            key="date",
                            component=DateField(uid="tally-col-date-field", key="date"),
                        ),
                        TableColumn(
                            uid="tally-col-policies",
                            label="Policies Sold",
                            key="policies",
                            component=TextField(
                                uid="tally-col-policies-field", key="policies"
                            ),
                        ),
                        TableColumn(
                            uid="tally-col-premium",
                            label="Premium",
                            key="premium",
                            component=TextField(
                                uid="tally-col-premium-field", key="premium"
                            ),
                        ),
                    ],
                ),
            ],
        )


# Detail View
@UIRegistry.register("tally.TallyDetail")
class TallyDetail(Component):
    def build(self):
        return ScaffoldLayout(
            uid="tally-detail-scaffold",
            sidebar_children=[UIRegistry.get("tally.TallyDetailMenu")().build()],
            children=[
                Detail(
                    uid="tally-detail-view",
                    key="tally",
                    children=[
                        Column(
                            uid="tally-detail-column",
                            children=[
                                TitleField(uid="tally-user", key="user"),
                                SubtitleField(uid="tally-date", key="date"),
                                Row(
                                    uid="tally-stats-row",
                                    classes="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 mt-4",
                                    children=[
                                        InlineLabel(
                                            uid="tally-visits-label",
                                            title="Visits",
                                            component=TextField(
                                                uid="tally-visits-val", key="visits"
                                            ),
                                        ),
                                        InlineLabel(
                                            uid="tally-appts-label",
                                            title="Appointments",
                                            component=TextField(
                                                uid="tally-appts-val",
                                                key="appointments",
                                            ),
                                        ),
                                        InlineLabel(
                                            uid="tally-leads-label",
                                            title="Leads",
                                            component=TextField(
                                                uid="tally-leads-val", key="leads"
                                            ),
                                        ),
                                        InlineLabel(
                                            uid="tally-calls-label",
                                            title="Calls",
                                            component=TextField(
                                                uid="tally-calls-val", key="calls"
                                            ),
                                        ),
                                        InlineLabel(
                                            uid="tally-demos-label",
                                            title="Demonstrations",
                                            component=TextField(
                                                uid="tally-demos-val", key="demos"
                                            ),
                                        ),
                                        InlineLabel(
                                            uid="tally-letters-label",
                                            title="Letters",
                                            component=TextField(
                                                uid="tally-letters-val", key="letters"
                                            ),
                                        ),
                                        InlineLabel(
                                            uid="tally-followups-label",
                                            title="Follow Ups",
                                            component=TextField(
                                                uid="tally-followups-val",
                                                key="follow_ups",
                                            ),
                                        ),
                                        InlineLabel(
                                            uid="tally-proposals-label",
                                            title="Proposals Given",
                                            component=TextField(
                                                uid="tally-proposals-val",
                                                key="proposals",
                                            ),
                                        ),
                                        InlineLabel(
                                            uid="tally-policies-label",
                                            title="Policies Sold",
                                            component=TextField(
                                                uid="tally-policies-val", key="policies"
                                            ),
                                        ),
                                        InlineLabel(
                                            uid="tally-premium-label",
                                            title="Premium",
                                            component=TextField(
                                                uid="tally-premium-val", key="premium"
                                            ),
                                        ),
                                    ],
                                ),
                            ],
                        ),
                    ],
                ),
            ],
        )


@UIRegistry.register("tally.TallyDeleteForm")
class TallyDeleteForm(Component):
    def build(self):
        return ScaffoldLayout(
            uid="tally-delete-scaffold",
            sidebar_children=[UIRegistry.get("tally.TallyDetailMenu")().build()],
            children=[
                DeleteConfirmation(
                    uid="tally-delete-confirmation",
                    key="tally",
                    title="Confirm Deletion",
                    message="Are you sure you want to delete this tally entry?",
                    cancel_url=lambda obj: reverse("tally:detail", args=[obj.pk]),
                ),
            ],
        )


# Dashboard
@UIRegistry.register("tally.TallyDashboard")
class TallyDashboard(Component):
    def build(self):
        return ScaffoldLayout(
            uid="tally-dashboard-scaffold",
            sidebar_children=[UIRegistry.get("tally.TallyMenu")().build()],
            children=[
                Form(
                    uid="tally-dashboard-filter",
                    role=["totschool_admin"],
                    action=reverse_lazy("tally:dashboard"),
                    target="#tally-dashboard-content",
                    method="get",
                    swap="morph",
                    classes="mb-4 border-b border-base-300 pb-4",
                    children=[
                        ForeignKeyInput(
                            uid="tally-dashboard-user",
                            key="user_id",
                            label="Agent",
                            model=User,
                            selection_url=reverse_lazy("users:select"),
                            placeholder="All Agents",
                            display_attr="name",
                        ),
                        Row(
                            uid="tally-dashboard-actions",
                            classes="flex gap-2",
                            children=[
                                SubmitInput(
                                    uid="tally-dashboard-submit",
                                    label="Apply",
                                ),
                                ClearInput(uid="tally-dashboard-clear", label="Clear"),
                            ],
                        ),
                    ],
                ),
                DashboardContent(
                    uid="tally-dashboard-content",
                ),
            ],
        )


# Leaderboard
@UIRegistry.register("tally.TallyLeaderboard")
class TallyLeaderboard(Component):
    def build(self):
        return ScaffoldLayout(
            uid="tally-leaderboard-scaffold",
            sidebar_children=[UIRegistry.get("tally.TallyMenu")().build()],
            children=[
                TitleField(uid="tally-leaderboard-title", key="title", classes="mb-4"),
                Form(
                    uid="tally-leaderboard-filter",
                    role=["totschool_admin"],
                    action=reverse_lazy("tally:leaderboard"),
                    target="#tally-leaderboard-content",
                    method="get",
                    swap="morph",
                    classes="mb-4 border-b border-base-300 pb-4",
                    children=[
                        ForeignKeyInput(
                            uid="tally-leaderboard-user",
                            key="user_id",
                            label="Highlight Agent",
                            model=User,
                            selection_url=reverse_lazy("users:select"),
                            placeholder="Select Agent to highlight",
                            display_attr="name",
                        ),
                        Row(
                            uid="tally-leaderboard-actions",
                            classes="flex gap-2",
                            children=[
                                SubmitInput(
                                    uid="tally-leaderboard-submit",
                                    label="Apply",
                                ),
                                ClearInput(
                                    uid="tally-leaderboard-clear", label="Clear"
                                ),
                            ],
                        ),
                    ],
                ),
                LeaderboardContent(
                    uid="tally-leaderboard-content",
                ),
            ],
        )
