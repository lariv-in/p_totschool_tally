from typing import List
from components.base import Component
from components import *  # noqa


def format_currency(amount):
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


class WhatsAppReport(Component):
    """Renders the WhatsApp sharing feature."""

    def __init__(self, classes: str = "", uid: str = "", role: List[str] = []):
        super().__init__(classes, uid, role)

    def render_html(self, **kwargs) -> str:
        report_data = kwargs.get("whatsapp_report")
        if report_data is None:
            return ""

        import urllib.parse
        from django.urls import reverse

        if not report_data.get("submitted"):
            daily_url = reverse("tally:daily")
            return f'''
            <div id="{self.uid}" class="bg-base-200 rounded-box border border-base-300 p-4 mb-4 {self.classes}">
                <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                    <div>
                        <h3 class="font-bold text-lg">Daily Report Not Submitted</h3>
                        <p class="text-base-content/70">You haven't submitted your daily report for today.</p>
                    </div>
                    <a href="{daily_url}" class="btn btn-primary" hx-boost="true">Fill Daily Report</a>
                </div>
            </div>
            '''

        date_str = report_data["date"].strftime("%d %b, %Y")
        metrics = [
            ("visits", "Visits", "total_visits"),
            ("appointments", "Appointments", "total_appointments"),
            ("leads", "Leads", "total_leads"),
            ("calls", "Calls", "total_calls"),
            ("demos", "Demonstrations", "total_demos"),
            ("letters", "Follow Up Letters", "total_letters"),
            ("followups", "Follow Ups", "total_follow_ups"),
            ("proposals", "Proposals Given", "total_proposals"),
            ("policies", "Policies Sold", "total_policies"),
            ("premium", "Premium", "total_premium"),
        ]

        today = report_data["today"]
        qtd = report_data["qtd"]
        lq = report_data["last_quarter"]

        message = "TOT School Report\n"
        message += f"Date: {date_str}\n"
        message += f"Name: {report_data['user_name']}\n\n"

        for p, label, key in metrics:
            today_val = today.get(key, 0)
            qtd_val = qtd.get(key, 0)
            lq_val = lq.get(key, 0)

            if key == "total_premium":
                message += f"- {label}: {format_currency(today_val)}/{format_currency(qtd_val)}/{format_currency(lq_val)}\n"
            else:
                message += f"- {label}: {today_val}/{qtd_val}/{lq_val}\n"

        encoded_message = urllib.parse.quote(message)
        whatsapp_url = f"https://wa.me/?text={encoded_message}"

        return f"""
        <div id="{self.uid}" class="bg-base-200 rounded-box border border-base-300 p-4 mb-4 {self.classes}">
            <h3 class="font-bold text-lg text-base-content mb-2">Today's Report Submitted!</h3>
            <textarea class="textarea textarea-bordered w-full h-[15rem] font-mono text-sm shadow-inner whitespace-pre overflow-y-auto mb-2" readonly>{message}</textarea>
            <a href="{whatsapp_url}" target="_blank" class="btn btn-sm btn-success text-white">Share on WhatsApp</a>
        </div>
        """


class LeaderboardCard(Component):
    """Component to render a metric-specific leaderboard."""

    def __init__(
        self,
        title: str,
        metric_key: str,
        format_as_currency: bool = False,
        classes: str = "",
        uid: str = "",
        role: List[str] = [],
    ):
        super().__init__(classes, uid, role)
        self.title = title
        self.metric_key = metric_key
        self.format_as_currency = format_as_currency

    def render_row(self, rank, name, value, highlight=False):
        val_str = format_currency(value) if self.format_as_currency else str(value)
        bg_class = (
            "bg-primary text-primary-content font-bold" if highlight else "bg-base-100"
        )
        return f"""
        <div class="flex justify-between items-center p-2 rounded {bg_class} mb-1 shadow-sm">
            <div class="flex items-center gap-2">
                <span class="w-6 text-center text-sm opacity-70">{"-" if rank == "-" else f"#{rank}"}</span>
                <span class="truncate max-w-[120px] sm:max-w-xs">{name}</span>
            </div>
            <span class="font-mono">{val_str}</span>
        </div>
        """

    def render_html(self, **kwargs) -> str:
        ldb = kwargs.get("leaderboards", {}).get(self.metric_key, {})
        top_5 = ldb.get("top_5", [])
        current_user = ldb.get("current_user")

        rows_html = []
        user_in_top_5 = False

        for entry in top_5:
            is_current = current_user and entry["user_id"] == current_user["user_id"]
            if is_current:
                user_in_top_5 = True
            rows_html.append(
                self.render_row(
                    entry["rank"],
                    entry["user_name"],
                    entry["value"],
                    highlight=is_current,
                )
            )

        if not rows_html:
            rows_html.append(
                '<div class="p-2 text-center text-sm opacity-50 italic">No data</div>'
            )

        out_of_top_5_html = ""
        if current_user and not user_in_top_5 and current_user["value"]:
            out_of_top_5_html = f"""
            <div class="divider my-1"></div>
            {self.render_row(current_user["rank"], current_user["user_name"], current_user["value"], highlight=True)}
            """

        return f'''
        <div id="{self.uid}" class="bg-base-200 rounded-box border border-base-300 p-4 {self.classes}">
            <h3 class="font-bold text-lg mb-4 pb-2 border-b border-base-300">{self.title}</h3>
            <div class="flex flex-col">
                {"".join(rows_html)}
                {out_of_top_5_html}
            </div>
        </div>
        '''


class LeaderboardContent(Component):
    """Container for the 4 leaderboard cards."""

    def __init__(self, classes: str = "", uid: str = "", role: List[str] = []):
        super().__init__(classes, uid, role)

    def render_html(self, **kwargs) -> str:
        cards = [
            LeaderboardCard(uid="ldb-visits", title="Top Visits", metric_key="visits"),
            LeaderboardCard(
                uid="ldb-demos", title="Top Demonstrations", metric_key="demos"
            ),
            LeaderboardCard(
                uid="ldb-policies", title="Top Policies Sold", metric_key="policies"
            ),
            LeaderboardCard(
                uid="ldb-premium",
                title="Top Premium",
                metric_key="premium",
                format_as_currency=True,
            ),
        ]

        rendered_cards = "".join([c.render_html(**kwargs) for c in cards])

        return f"""
        <div id="{self.uid}" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 xl:grid-cols-4 gap-4 {self.classes}">
            {rendered_cards}
        </div>
        """


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
        role: List[str] = [],
    ):
        super().__init__(classes, uid, role)
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


class DashboardContent(Component):
    """Renders the full dashboard layout with Performance Summary and Detailed Metrics.

    Reads the 'dashboard' dict from kwargs to populate stat cards.
    """

    def __init__(self, classes: str = "", uid: str = "", role: List[str] = []):
        super().__init__(classes, uid, role)

    def render_html(self, **kwargs) -> str:
        d = kwargs.get("dashboard", {})

        metrics_cards = Column(
            uid="metrics-cards-column",
            classes="mb-4",
            children=[
                TitleField(
                    uid="metrics-cards-title",
                    static_value="Performance Summary",
                ),
                SubtitleField(
                    uid="metrics-cards-subtitle",
                    static_value="Analysis of the current quarter",
                ),
                Row(
                    uid="metrics-cards-row",
                    classes="grid grid-cols-2 lg:grid-cols-4 gap-2 my-2",
                    children=[
                        StatCard(
                            uid="dash-appt-visit",
                            title="Appt. conversion",
                            value=f"{d.get('appt_visit_ratio', 0)}%",
                            description="Appt. / Visit Ratio",
                        ),
                        StatCard(
                            uid="dash-demo-appt",
                            title="Demo conversion",
                            value=f"{d.get('demo_appt_ratio', 0)}%",
                            description="Demo / Appt. Ratio",
                        ),
                        StatCard(
                            uid="dash-policy-demo",
                            title="Policy conversion",
                            value=f"{d.get('policy_demo_ratio', 0)}%",
                            description="Policy / Demo Ratio",
                        ),
                        StatCard(
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
            ("visits", "Visits", "total_visits"),
            ("appointments", "Appointments", "total_appointments"),
            ("leads", "Leads", "total_leads"),
            ("calls", "Calls", "total_calls"),
            ("demos", "Demonstrations", "total_demos"),
            ("letters", "Follow Up Letters", "total_letters"),
            ("followups", "Follow Ups", "total_follow_ups"),
            ("proposals", "Proposals Given", "total_proposals"),
            ("policies", "Policies Sold", "total_policies"),
        ]

        tally_stats = Column(
            uid="tally-stats-column",
            children=[
                TitleField(
                    uid="tally-stats-title",
                    static_value="Statistics",
                ),
                SubtitleField(
                    uid="tally-stats-subtitle",
                    static_value="Totals for the current quarter",
                ),
                Row(
                    uid="tally-stats-row",
                    classes="grid grid-cols-2 md:grid-cols-3 gap-2 my-2",
                    children=[
                        StatCard(
                            uid=f"dash-{metric[0]}",
                            title=metric[1],
                            value=d.get(metric[2], 0),
                            description="",
                        )
                        for metric in metrics
                    ],
                ),
                StatCard(
                    uid="dash-premium",
                    title="Premium",
                    value=format_currency(d.get("total_premium", 0)),
                    description="",
                    color="success",
                ),
            ],
        ).render_html(**kwargs)

        whatsapp_section = WhatsAppReport(uid="dash-whatsapp-report").render_html(
            **kwargs
        )

        return f"""
        <div id="{self.uid}">
            {whatsapp_section}
            {metrics_cards}
            {tally_stats}
        </div>
        """
