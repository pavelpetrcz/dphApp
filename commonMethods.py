import time
from datetime import date


def getTodayDateAsString():
    """
    Today date as a string dd.mm.yyyy
    :return:
    """
    today = date.today()
    return today.strftime("%d.%m.%Y")


def getThisYear():
    """
    get this year - example string "2021"
    :return: string with year
    """
    return time.strftime("%Y")
