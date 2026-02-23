from django.urls import reverse_lazy, reverse
from lariv.registry import UIRegistry, ComponentRegistry, EnvironmentRegistry
from lariv.environment import Environment, EnvironmentField
from users.models import User
from django.utils import timezone
from .models import TotSchoolSession


@EnvironmentRegistry.register("tally")
class TallyEnvironment(Environment):
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
UIRegistry.register("tally.TallyMenu")(
    ComponentRegistry.get("menu")(
        uid="tally-menu",
        title="Tally",
        back=ComponentRegistry.get("menu_item")(
            uid="tally-menu-back",
            title="Back to All Apps",
            url=reverse_lazy("apps"),
        ),
        children=[
            ComponentRegistry.get("menu_item")(
                uid="tally-menu-dashboard",
                title="Dashboard",
                url=reverse_lazy("tally:dashboard"),
            ),
            ComponentRegistry.get("menu_item")(
                uid="tally-menu-list",
                title="All Reports",
                url=reverse_lazy("tally:list"),
            ),
            ComponentRegistry.get("menu_item")(
                uid="tally-menu-daily",
                title="Fill Daily Report",
                url=reverse_lazy("tally:daily"),
            ),
            ComponentRegistry.get("menu_item")(
                uid="tally-menu-create",
                title="Create Tally (Admin)",
                role=["totschool_admin"],
                url=reverse_lazy("tally:create"),
            ),
        ],
    )
)

UIRegistry.register("tally.TallyDetailMenu")(
    ComponentRegistry.get("menu")(
        uid="tally-detail-menu",
        back=ComponentRegistry.get("menu_item")(
            uid="tally-detail-menu-back",
            title="Back to all Tallies",
            url=reverse_lazy("tally:default"),
        ),
        key="tally",
        title=lambda o: f"Tally: {o.user.name} ({o.date})",
        children=[
            ComponentRegistry.get("menu_item")(
                uid="tally-detail-menu-detail",
                title="Tally Detail",
                key="tally",
                url=lambda o: reverse("tally:detail", args=[o.pk]),
            ),
            ComponentRegistry.get("menu_item")(
                uid="tally-detail-menu-edit",
                title="Edit Tally",
                key="tally",
                url=lambda o: reverse("tally:update", args=[o.pk]),
            ),
            ComponentRegistry.get("menu_item")(
                uid="tally-detail-menu-delete",
                title="Delete Tally",
                key="tally",
                url=lambda o: reverse("tally:delete", args=[o.pk]),
            ),
        ],
    )
)

# Filters for Tally
UIRegistry.register("tally.TallyFilter")(
    ComponentRegistry.get("form")(
        uid="tally-filter",
        action=reverse_lazy("tally:list"),
        target="#tally-table_display_content",
        method="get",
        swap="morph",
        children=[
            ComponentRegistry.get("foreign_key_input")(
                uid="tally-filter-user",
                key="user",
                label="User",
                model=User,
                selection_url=reverse_lazy("users:select"),
                placeholder="Select User",
            ),
            ComponentRegistry.get("date_input")(
                uid="tally-filter-date", key="date", label="Date"
            ),
            ComponentRegistry.get("row")(
                uid="tally-filter-actions",
                classes="flex gap-2",
                children=[
                    ComponentRegistry.get("submit_input")(
                        uid="tally-filter-submit",
                        label="Apply",
                    ),
                    ComponentRegistry.get("clear_input")(
                        uid="tally-filter-clear", label="Clear"
                    ),
                ],
            ),
        ],
    )
)


# Forms for Tally
class DynamicDate:
    def __str__(self):
        return timezone.now().date().strftime("%b %d, %Y")


def get_tally_common_fields(prefix):
    return [
        ComponentRegistry.get("row")(
            uid=f"{prefix}-visits-appts",
            classes="grid grid-cols-1 gap-1 @md:grid-cols-2",
            children=[
                ComponentRegistry.get("text_input")(
                    uid=f"{prefix}-visits", key="visits", label="Visits", required=True
                ),
                ComponentRegistry.get("text_input")(
                    uid=f"{prefix}-appointments",
                    key="appointments",
                    label="Appointments",
                    required=True,
                ),
            ],
        ),
        ComponentRegistry.get("row")(
            uid=f"{prefix}-leads-calls",
            classes="grid grid-cols-1 gap-1 @md:grid-cols-2",
            children=[
                ComponentRegistry.get("text_input")(
                    uid=f"{prefix}-leads", key="leads", label="Leads", required=True
                ),
                ComponentRegistry.get("text_input")(
                    uid=f"{prefix}-calls",
                    key="calls",
                    label="Calls",
                    required=True,
                ),
            ],
        ),
        ComponentRegistry.get("row")(
            uid=f"{prefix}-demos-letters",
            classes="grid grid-cols-1 gap-1 @md:grid-cols-2",
            children=[
                ComponentRegistry.get("text_input")(
                    uid=f"{prefix}-demos",
                    key="demos",
                    label="Demonstrations",
                    required=True,
                ),
                ComponentRegistry.get("text_input")(
                    uid=f"{prefix}-letters",
                    key="letters",
                    label="Follow Up Letters Sent",
                    required=True,
                ),
            ],
        ),
        ComponentRegistry.get("row")(
            uid=f"{prefix}-followups-proposals",
            classes="grid grid-cols-1 gap-1 @md:grid-cols-2",
            children=[
                ComponentRegistry.get("text_input")(
                    uid=f"{prefix}-followups",
                    key="follow_ups",
                    label="Follow Ups",
                    required=True,
                ),
                ComponentRegistry.get("text_input")(
                    uid=f"{prefix}-proposals",
                    key="proposals",
                    label="Proposals Given",
                    required=True,
                ),
            ],
        ),
        ComponentRegistry.get("row")(
            uid=f"{prefix}-policies-premium",
            classes="grid grid-cols-1 gap-1 @md:grid-cols-2",
            children=[
                ComponentRegistry.get("text_input")(
                    uid=f"{prefix}-policies",
                    key="policies",
                    label="Policies Sold",
                    required=True,
                ),
                ComponentRegistry.get("text_input")(
                    uid=f"{prefix}-premium",
                    key="premium",
                    label="Premium",
                    required=True,
                ),
            ],
        ),
    ]


TallyFormFields = ComponentRegistry.get("form")(
    uid="tally-form",
    action=lambda obj: (
        reverse("tally:update", args=[obj.pk])
        if getattr(obj, "pk", None)
        else reverse("tally:create")
    ),
    target="#app-layout",
    key="tally",
    title="Tally Form",
    subtitle="Log Daily Performance",
    classes="@container",
    children=[
        ComponentRegistry.get("row")(
            uid="tally-form-user-row",
            classes="grid grid-cols-1 gap-1 @md:grid-cols-2",
            children=[
                ComponentRegistry.get("foreign_key_input")(
                    uid="tally-form-user",
                    key="user",
                    label="Agent",
                    selection_url=reverse_lazy("users:select"),
                    display_attr="name",
                    placeholder="Select Agent",
                    required=True,
                    model=User,
                ),
                ComponentRegistry.get("date_input")(
                    uid="tally-form-date",
                    key="date",
                    label="Date",
                    required=True,
                ),
            ],
        ),
        *get_tally_common_fields("tally-form"),
        ComponentRegistry.get("submit_input")(uid="tally-form-submit", label="Save"),
    ],
)

UIRegistry.register("tally.TallyCreateForm")(
    ComponentRegistry.get("scaffold")(
        uid="tally-create-scaffold",
        sidebar_children=[UIRegistry.get("tally.TallyMenu")],
        children=[TallyFormFields],
    )
)

UIRegistry.register("tally.TallyUpdateForm")(
    ComponentRegistry.get("scaffold")(
        uid="tally-update-scaffold",
        sidebar_children=[UIRegistry.get("tally.TallyDetailMenu")],
        children=[TallyFormFields],
    )
)

TallyDailyFormFields = ComponentRegistry.get("form")(
    uid="tally-daily-form",
    action=lambda obj: reverse("tally:daily"),
    target="#app-layout",
    key="tally",
    title="Daily Report",
    subtitle=DynamicDate(),
    classes="@container",
    children=[
        *get_tally_common_fields("tally-daily-form"),
        ComponentRegistry.get("submit_input")(
            uid="tally-daily-form-submit", label="Save"
        ),
    ],
)

UIRegistry.register("tally.TallyDailyForm")(
    ComponentRegistry.get("scaffold")(
        uid="tally-daily-scaffold",
        sidebar_children=[UIRegistry.get("tally.TallyMenu")],
        children=[TallyDailyFormFields],
    )
)

# Tally Table
UIRegistry.register("tally.TallyTable")(
    ComponentRegistry.get("scaffold")(
        uid="tally-table-scaffold",
        sidebar_children=[UIRegistry.get("tally.TallyMenu")],
        children=[
            ComponentRegistry.get("table")(
                uid="tally-table",
                classes="w-full",
                key="tallies",
                title="Tallies",
                subtitle="All Daily Reports",
                row_url=lambda o: reverse("tally:detail", args=[o.pk]),
                filter_component=UIRegistry.get("tally.TallyFilter"),
                columns=[
                    ComponentRegistry.get("table_column")(
                        uid="tally-col-user",
                        label="Agent",
                        key="user",
                        component=ComponentRegistry.get("text_field")(
                            uid="tally-col-user-field", key="user"
                        ),
                    ),
                    ComponentRegistry.get("table_column")(
                        uid="tally-col-date",
                        label="Date",
                        key="date",
                        component=ComponentRegistry.get("date_field")(
                            uid="tally-col-date-field", key="date"
                        ),
                    ),
                    ComponentRegistry.get("table_column")(
                        uid="tally-col-policies",
                        label="Policies Sold",
                        key="policies",
                        component=ComponentRegistry.get("text_field")(
                            uid="tally-col-policies-field", key="policies"
                        ),
                    ),
                    ComponentRegistry.get("table_column")(
                        uid="tally-col-premium",
                        label="Premium",
                        key="premium",
                        component=ComponentRegistry.get("text_field")(
                            uid="tally-col-premium-field", key="premium"
                        ),
                    ),
                ],
            )
        ],
    )
)

# Detail View
UIRegistry.register("tally.TallyDetail")(
    ComponentRegistry.get("scaffold")(
        uid="tally-detail-scaffold",
        sidebar_children=[UIRegistry.get("tally.TallyDetailMenu")],
        children=[
            ComponentRegistry.get("detail")(
                uid="tally-detail-view",
                key="tally",
                children=[
                    ComponentRegistry.get("column")(
                        uid="tally-detail-column",
                        children=[
                            ComponentRegistry.get("title_field")(
                                uid="tally-user", key="user"
                            ),
                            ComponentRegistry.get("subtitle_field")(
                                uid="tally-date", key="date"
                            ),
                            ComponentRegistry.get("row")(
                                uid="tally-stats-row",
                                classes="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 mt-4",
                                children=[
                                    ComponentRegistry.get("inline_label")(
                                        uid="tally-visits-label",
                                        title="Visits",
                                        component=ComponentRegistry.get("text_field")(
                                            uid="tally-visits-val", key="visits"
                                        ),
                                    ),
                                    ComponentRegistry.get("inline_label")(
                                        uid="tally-appts-label",
                                        title="Appointments",
                                        component=ComponentRegistry.get("text_field")(
                                            uid="tally-appts-val", key="appointments"
                                        ),
                                    ),
                                    ComponentRegistry.get("inline_label")(
                                        uid="tally-leads-label",
                                        title="Leads",
                                        component=ComponentRegistry.get("text_field")(
                                            uid="tally-leads-val", key="leads"
                                        ),
                                    ),
                                    ComponentRegistry.get("inline_label")(
                                        uid="tally-calls-label",
                                        title="Calls",
                                        component=ComponentRegistry.get("text_field")(
                                            uid="tally-calls-val", key="calls"
                                        ),
                                    ),
                                    ComponentRegistry.get("inline_label")(
                                        uid="tally-demos-label",
                                        title="Demonstrations",
                                        component=ComponentRegistry.get("text_field")(
                                            uid="tally-demos-val", key="demos"
                                        ),
                                    ),
                                    ComponentRegistry.get("inline_label")(
                                        uid="tally-letters-label",
                                        title="Letters",
                                        component=ComponentRegistry.get("text_field")(
                                            uid="tally-letters-val", key="letters"
                                        ),
                                    ),
                                    ComponentRegistry.get("inline_label")(
                                        uid="tally-followups-label",
                                        title="Follow Ups",
                                        component=ComponentRegistry.get("text_field")(
                                            uid="tally-followups-val", key="follow_ups"
                                        ),
                                    ),
                                    ComponentRegistry.get("inline_label")(
                                        uid="tally-proposals-label",
                                        title="Proposals Given",
                                        component=ComponentRegistry.get("text_field")(
                                            uid="tally-proposals-val", key="proposals"
                                        ),
                                    ),
                                    ComponentRegistry.get("inline_label")(
                                        uid="tally-policies-label",
                                        title="Policies Sold",
                                        component=ComponentRegistry.get("text_field")(
                                            uid="tally-policies-val", key="policies"
                                        ),
                                    ),
                                    ComponentRegistry.get("inline_label")(
                                        uid="tally-premium-label",
                                        title="Premium",
                                        component=ComponentRegistry.get("text_field")(
                                            uid="tally-premium-val", key="premium"
                                        ),
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
            )
        ],
    )
)

UIRegistry.register("tally.TallyDeleteForm")(
    ComponentRegistry.get("scaffold")(
        uid="tally-delete-scaffold",
        sidebar_children=[UIRegistry.get("tally.TallyDetailMenu")],
        children=[
            ComponentRegistry.get("delete_confirmation")(
                uid="tally-delete-confirmation",
                key="tally",
                title="Confirm Deletion",
                message="Are you sure you want to delete this tally entry?",
                cancel_url=lambda obj: reverse("tally:detail", args=[obj.pk]),
            ),
        ],
    )
)

# Dashboard
UIRegistry.register("tally.TallyDashboard")(
    ComponentRegistry.get("scaffold")(
        uid="tally-dashboard-scaffold",
        sidebar_children=[UIRegistry.get("tally.TallyMenu")],
        children=[
            ComponentRegistry.get("form")(
                uid="tally-dashboard-filter",
                role=["totschool_admin"],
                action=reverse_lazy("tally:dashboard"),
                target="#tally-dashboard-content",
                method="get",
                swap="morph",
                classes="mb-4 border-b border-base-300 pb-4",
                children=[
                    ComponentRegistry.get("foreign_key_input")(
                        uid="tally-dashboard-user",
                        key="user_id",
                        label="Agent",
                        model=User,
                        selection_url=reverse_lazy("users:select"),
                        placeholder="All Agents",
                        display_attr="name",
                    ),
                    ComponentRegistry.get("row")(
                        uid="tally-dashboard-actions",
                        classes="flex gap-2",
                        children=[
                            ComponentRegistry.get("submit_input")(
                                uid="tally-dashboard-submit",
                                label="Apply",
                            ),
                            ComponentRegistry.get("clear_input")(
                                uid="tally-dashboard-clear", label="Clear"
                            ),
                        ],
                    ),
                ],
            ),
            ComponentRegistry.get("dashboard_content")(
                uid="tally-dashboard-content",
            ),
        ],
    )
)
