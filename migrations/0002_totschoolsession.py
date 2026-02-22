from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("p_totschool_tally", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="TotSchoolSession",
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
                ("name", models.CharField(max_length=250)),
                ("start", models.DateField()),
                ("end", models.DateField()),
            ],
        ),
    ]
