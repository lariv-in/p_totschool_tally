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
    def get_dashboard_stats(self, user_id=None):
        queryset = self.all()
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

        return totals


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
