import datetime
from .models import TotSchoolSession


def get_quarter_details_for_date(date):
    year = date.year
    quarter = (date.month - 1) // 3 + 1

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
    return name, start_date, end_date


def ensure_session_for_date(date):
    name, start_date, end_date = get_quarter_details_for_date(date)
    session, created = TotSchoolSession.objects.get_or_create(
        name=name, defaults={"start": start_date, "end": end_date}
    )
    return session
