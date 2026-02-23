from django.db import models
from django.db.models import Sum, Count, Value, IntegerField
from django.db.models.functions import Coalesce
from django.utils import timezone
from users.models import User
from django.urls import reverse


def get_current_date():
    """Get current date in the configured timezone"""
    return timezone.now().date()


class TallyManager(models.Manager):
    def get_dashboard_stats(self, user_id=None, session=None):
        queryset = self.all()
        if user_id:
            queryset = queryset.filter(user=user_id)
        if session:
            queryset = queryset.filter(date__gte=session.start, date__lte=session.end)

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

        return totals

    def get_whatsapp_report_data(self, user_id=None):
        if not user_id:
            return None

        today = timezone.now().date()
        today_qs = self.filter(user=user_id, date=today)

        if not today_qs.exists():
            return {"submitted": False}

        from .utils import ensure_session_for_date
        import datetime

        class DummySession:
            def __init__(self, start, end):
                self.start = start
                self.end = end

        today_session = DummySession(today, today)
        today_totals = self.get_dashboard_stats(user_id=user_id, session=today_session)

        current_quarter = ensure_session_for_date(today)
        qtd_session = DummySession(current_quarter.start, today)
        qtd_totals = self.get_dashboard_stats(user_id=user_id, session=qtd_session)

        last_quarter_date = current_quarter.start - datetime.timedelta(days=1)
        last_quarter_session = ensure_session_for_date(last_quarter_date)
        last_quarter_totals = self.get_dashboard_stats(
            user_id=user_id, session=last_quarter_session
        )

        user = User.objects.get(id=user_id)

        return {
            "submitted": True,
            "today": today_totals,
            "qtd": qtd_totals,
            "last_quarter": last_quarter_totals,
            "user_name": user.name,
            "date": today,
        }

    def get_leaderboards(self, user_id=None, session=None):
        queryset = self.all()
        if session:
            queryset = queryset.filter(date__gte=session.start, date__lte=session.end)

        # Aggregate totals per user
        user_totals = queryset.values("user__id", "user__name").annotate(
            total_visits=Coalesce(Sum("visits"), Value(0), output_field=IntegerField()),
            total_demos=Coalesce(Sum("demos"), Value(0), output_field=IntegerField()),
            total_policies=Coalesce(
                Sum("policies"), Value(0), output_field=IntegerField()
            ),
            total_premium=Coalesce(
                Sum("premium"), Value(0), output_field=IntegerField()
            ),
        )

        metrics = [
            ("visits", "total_visits"),
            ("demos", "total_demos"),
            ("policies", "total_policies"),
            ("premium", "total_premium"),
        ]

        leaderboards = {}

        for metric_name, field_name in metrics:
            # Sort all users by the specific metric
            sorted_totals = sorted(
                user_totals, key=lambda x: x[field_name], reverse=True
            )

            top_5 = []
            user_entry = None

            for index, row in enumerate(sorted_totals):
                rank = index + 1
                entry = {
                    "rank": rank,
                    "user_id": row["user__id"],
                    "user_name": row["user__name"],
                    "value": row[field_name],
                }

                if rank <= 5:
                    top_5.append(entry)

                if user_id and row["user__id"] == user_id:
                    user_entry = entry

            # If user has no tallies in session, create a default 0 entry for them
            if user_id and not user_entry:
                try:
                    user = User.objects.get(id=user_id)
                    user_entry = {
                        "rank": "-",
                        "user_id": user.id,
                        "user_name": user.name,
                        "value": 0,
                    }
                except User.DoesNotExist:
                    user_entry = None

            leaderboards[metric_name] = {
                "top_5": top_5,
                "current_user": user_entry,
            }

        return leaderboards


class Tally(models.Model):
    objects = TallyManager()

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tallies")
    date = models.DateField(default=get_current_date)

    # Tracking fields
    visits = models.IntegerField(default=0, help_text="Visits")
    appointments = models.IntegerField(default=0, help_text="Appointments")
    leads = models.IntegerField(default=0, help_text="Leads")
    calls = models.IntegerField(default=0, help_text="Calls")
    demos = models.IntegerField(default=0, help_text="Demonstrations")
    letters = models.IntegerField(default=0, help_text="Follow Up Letters Sent")
    follow_ups = models.IntegerField(default=0, help_text="Follow Ups")
    proposals = models.IntegerField(default=0, help_text="Brahmastra Proposals Given")
    policies = models.IntegerField(default=0, help_text="Policies Sold")
    premium = models.IntegerField(default=0, help_text="Premium")

    class Meta:
        unique_together = ["user", "date"]
        ordering = ["-date"]

    def __str__(self):
        return f"{self.user.name} - {self.date}"

    def get_absolute_url(self):
        return reverse("tally:detail", kwargs={"pk": self.pk})


class TotSchoolSession(models.Model):
    name = models.CharField(max_length=250, unique=True)
    start = models.DateField()
    end = models.DateField()

    @property
    def is_active(self):
        return self.start <= timezone.now().date() <= self.end

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("totschool_sessions:detail", kwargs={"pk": self.pk})
