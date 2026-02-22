from django.apps import AppConfig


class TotschoolTallyConfig(AppConfig):
    name = "p_totschool_tally"
    p_type = "app"
    verbose_name = "Progress Tracker"
    url_prefix = "tally"
    icon = "chart-bar"

    def ready(self):
        from . import components, ui  # noqa: F401
