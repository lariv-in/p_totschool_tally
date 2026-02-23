from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import Tally, TotSchoolSession


@admin.register(Tally)
class TallyAdmin(ImportExportModelAdmin):
    list_display = (
        "user",
        "date",
        "visits",
        "appointments",
        "leads",
        "calls",
        "demos",
        "letters",
        "follow_ups",
        "proposals",
        "policies",
        "premium",
    )
    list_filter = ("date", "user")
    search_fields = ("user__name", "user__email", "user__phone")
    date_hierarchy = "date"


@admin.register(TotSchoolSession)
class TotSchoolSessionAdmin(ImportExportModelAdmin):
    list_display = ("name", "start", "end")
    search_fields = ("name",)
    list_filter = ("start", "end")
