from django.db import models
from django.utils import timezone
from users.models import User


def get_current_date():
    """Get current date in the configured timezone"""
    return timezone.now().date()


class Tally(models.Model):
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
        from django.urls import reverse

        return reverse("tally:detail", kwargs={"pk": self.pk})
