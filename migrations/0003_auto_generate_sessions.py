from django.db import migrations, models
import datetime
from django.utils import timezone


def generate_sessions_from_2024(apps, schema_editor):
    TotSchoolSession = apps.get_model("p_totschool_tally", "TotSchoolSession")

    current_date = timezone.now().date()
    year = 2024
    quarter = 1

    while True:
        start_date = datetime.date(year, (quarter - 1) * 3 + 1, 1)
        next_quarter = quarter + 1
        if next_quarter > 4:
            next_quarter_year = year + 1
            next_quarter_month = 1
        else:
            next_quarter_year = year
            next_quarter_month = (next_quarter - 1) * 3 + 1

        end_date = datetime.date(
            next_quarter_year, next_quarter_month, 1
        ) - datetime.timedelta(days=1)
        name = f"{year} Quarter {quarter}"

        TotSchoolSession.objects.get_or_create(
            name=name, defaults={"start": start_date, "end": end_date}
        )

        # Keep generating until we create the session covering the current date
        if end_date >= current_date:
            break

        quarter += 1
        if quarter > 4:
            quarter = 1
            year += 1


class Migration(migrations.Migration):
    dependencies = [
        ("p_totschool_tally", "0002_totschoolsession"),
    ]

    operations = [
        migrations.RunPython(generate_sessions_from_2024, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="totschoolsession",
            name="name",
            field=models.CharField(max_length=250, unique=True),
        ),
    ]
