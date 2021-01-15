from datetime import date, timedelta

from shopping_list.app.calendar import get_dates, TIME_SPAN


def test_get_dates(mocker):
    dates = get_dates()
    assert len(dates) == TIME_SPAN
    assert dates[0] == date.today()


def test_get_dates_change_timespan(mocker):
    mocker.patch('shopping_list.app.calendar.TIME_SPAN', 5)
    dates = get_dates()
    assert len(dates) == 5
    assert dates[0] == date.today()


def test_get_dates_change_today(mocker):
    tomorrow = date.today() + timedelta(days=1)
    mocker.patch('shopping_list.app.calendar.date_now', return_value=tomorrow)
    dates = get_dates()
    assert len(dates) == TIME_SPAN
    assert dates[0] == tomorrow
