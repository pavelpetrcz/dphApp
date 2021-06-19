from datetime import date


def getTodayDateAsString():
    """
    Today date as a string dd.mm.yyyy
    :return:
    """
    today = date.today()
    return today.strftime("%d.%m.%Y")
