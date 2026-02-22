from lariv.registry import ComponentRegistry
from components.base import Component


@ComponentRegistry.register("stat_card")
class StatCard(Component):
    """A stat card component that displays a metric value with title and optional description.

    Parameters:
        title: The label for the stat (e.g., "Policies Sold")
        value: The value to display (e.g., "42" or "85.5%")
        description: Optional subtitle/description text
        color: DaisyUI color class (primary, secondary, accent, success, warning, error, info)
    """

    def __init__(
        self,
        title: str = "",
        value: str = "",
        description: str = "",
        color: str = "",
        classes: str = "",
        uid: str = "",
    ):
        super().__init__(classes, uid)
        self.title = title
        self.value = value
        self.description = description
        self.color = color

    def render_html(self, **kwargs) -> str:
        description_html = (
            f'<div class="stat-desc">{self.description}</div>'
            if self.description
            else ""
        )

        return f"""
        <div id="{self.uid}" class="stat bg-base-100 rounded-box border border-base-300 {self.classes}">
            <div class="stat-title text-md font-bold">{self.title}</div>
            <div class="text-{self.color} text-lg font-bold">{self.value}</div>
            {description_html}
        </div>
        """


@ComponentRegistry.register("dashboard_content")
class DashboardContent(Component):
    """Renders the full dashboard layout with Performance Summary and Detailed Metrics.

    Reads the 'dashboard' dict from kwargs to populate stat cards.
    """

    def __init__(self, classes: str = "", uid: str = ""):
        super().__init__(classes, uid)

    def _format_currency(self, amount):
        """Format number in Indian currency style."""
        if amount == 0:
            return "₹0"
        s = str(amount)
        if len(s) <= 3:
            return f"₹{s}"
        result = s[-3:]
        s = s[:-3]
        while s:
            result = s[-2:] + "," + result
            s = s[:-2]
        return f"₹{result}"

    def render_html(self, **kwargs) -> str:
        d = kwargs.get("dashboard", {})

        metrics_cards = ComponentRegistry.get("column")(
            uid="metrics-cards-column",
            classes="mb-4",
            children=[
                ComponentRegistry.get("title_field")(
                    uid="metrics-cards-title",
                    static_value="Performance Summary",
                ),
                ComponentRegistry.get("subtitle_field")(
                    uid="metrics-cards-subtitle",
                    static_value="Analysis of the current period",
                ),
                ComponentRegistry.get("row")(
                    uid="metrics-cards-row",
                    classes="grid grid-cols-2 lg:grid-cols-4 gap-2 my-2",
                    children=[
                        ComponentRegistry.get("stat_card")(
                            uid="dash-appt-visit",
                            title="Appt. conversion",
                            value=f"{d.get('appt_visit_ratio', 0)}%",
                            description="Appt. / Visit Ratio",
                        ),
                        ComponentRegistry.get("stat_card")(
                            uid="dash-demo-appt",
                            title="Demo conversion",
                            value=f"{d.get('demo_appt_ratio', 0)}%",
                            description="Demo / Appt. Ratio",
                        ),
                        ComponentRegistry.get("stat_card")(
                            uid="dash-policy-demo",
                            title="Policy conversion",
                            value=f"{d.get('policy_demo_ratio', 0)}%",
                            description="Policy / Demo Ratio",
                        ),
                        ComponentRegistry.get("stat_card")(
                            uid="dash-forms-filled",
                            title="Forms Filled",
                            value=str(d.get("forms_filled", 0)),
                            description="",
                        ),
                    ],
                ),
            ],
        ).render_html(**kwargs)

        metrics = [
            ("calls", "Calls", "total_calls"),
            ("leads", "Leads", "total_leads"),
            ("visits", "Visits", "total_visits"),
            ("appointments", "Appointments", "total_appointments"),
            ("demos", "Demonstrations", "total_demos"),
            ("letters", "Follow Up Letters", "total_letters"),
            ("followups", "Follow Ups", "total_follow_ups"),
            ("proposals", "Proposals Given", "total_proposals"),
            ("policies", "Policies Sold", "total_policies"),
        ]

        tally_stats = ComponentRegistry.get("column")(
            uid="tally-stats-column",
            children=[
                ComponentRegistry.get("title_field")(
                    uid="tally-stats-title",
                    static_value="Statistics",
                ),
                ComponentRegistry.get("subtitle_field")(
                    uid="tally-stats-subtitle",
                    static_value="Totals for the current period",
                ),
                ComponentRegistry.get("row")(
                    uid="tally-stats-row",
                    classes="grid grid-cols-2 md:grid-cols-3 gap-2 my-2",
                    children=[
                        ComponentRegistry.get("stat_card")(
                            uid=f"dash-{metric[0]}",
                            title=metric[1],
                            value=d.get(metric[2], 0),
                            description="",
                        )
                        for metric in metrics
                    ],
                ),
                ComponentRegistry.get("stat_card")(
                    uid="dash-premium",
                    title="Premium",
                    value=self._format_currency(d.get("total_premium", 0)),
                    description="",
                    color="success",
                ),
            ],
        ).render_html(**kwargs)

        return f"""
        <div id="{self.uid}">
            {metrics_cards}
            {tally_stats}
        </div>
        """
