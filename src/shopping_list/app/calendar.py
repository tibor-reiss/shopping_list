from datetime import date, timedelta


TIME_SPAN = 14


def date_now():  # cannot directly mock date
    return date.today()


def get_dates():
    now = date_now()
    dates = []
    for i in range(0, TIME_SPAN):
        day = now + timedelta(days=i)
        dates.append(day)
    return dates
