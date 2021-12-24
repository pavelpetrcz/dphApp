import time
from datetime import date

import commonMethods


def test_getTodayDateAsString():
    today = date.today()
    assert commonMethods.getTodayDateAsString() == today.strftime("%d.%m.%Y")


def test_getThisYear():
    if time.strftime("%m") == "1":
        assert commonMethods.getThisYear() == str(int(time.strftime("%Y")) - 1)
    else:
        assert commonMethods.getThisYear() == str(int(time.strftime("%Y")))



