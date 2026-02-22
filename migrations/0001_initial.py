import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

import p_totschool_tally.models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Tally",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "date",
                    models.DateField(default=p_totschool_tally.models.get_current_date),
                ),
                ("calls", models.IntegerField(default=0, help_text="Calls")),
                ("leads", models.IntegerField(default=0, help_text="Leads")),
                ("visits", models.IntegerField(default=0, help_text="Visits")),
                (
                    "appointments",
                    models.IntegerField(default=0, help_text="Appointments"),
                ),
                (
                    "demos",
                    models.IntegerField(default=0, help_text="Demonstrations"),
                ),
                (
                    "letters",
                    models.IntegerField(default=0, help_text="Follow Up Letters Sent"),
                ),
                ("follow_ups", models.IntegerField(default=0, help_text="Follow Ups")),
                (
                    "proposals",
                    models.IntegerField(
                        default=0, help_text="Brahmastra Proposals Given"
                    ),
                ),
                ("policies", models.IntegerField(default=0, help_text="Policies Sold")),
                ("premium", models.IntegerField(default=0, help_text="Premium")),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="tallies",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-date"],
                "unique_together": {("user", "date")},
            },
        ),
    ]
