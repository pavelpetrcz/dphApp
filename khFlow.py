import logging
import os
import lxml.etree as et
import pandas as pd

import commonMethods


def execute(numMonth, year, khOutputLoc, khTempFile):
    """
    :param numMonth: numeric value of month (1-12)
    :param year: numeric value of year (2021)
    :param khOutputLoc: where to save final XML file
    :param khTempFile: templete to override
    """
    tree = et.parse(khTempFile)
    root = tree.getroot()
    DPHKH1 = root.find("DPHKH1")

    # load source data
    incomes = pd.read_excel("A://OSVC//dph//evidence.xlsx", sheet_name="prijmy", engine='openpyxl')
    expenses = pd.read_excel("A://OSVC//dph//evidence.xlsx", sheet_name="vydaje", engine='openpyxl')

    # Changes in XML template
    # VetaD (mesic - param mesic, rok - rok, datum vystavení - d_poddp)
    datum_podani = commonMethods.getTodayDateAsString()

    DPHKH1.find("VetaD").set("mesic", str(numMonth))
    DPHKH1.find("VetaD").set("rok", str(year))
    DPHKH1.find("VetaD").set("d_poddp", datum_podani)

    # Incomes
    # VetaA4+A5
    num = 1
    obrat = 0
    dan = 0
    obrat15 = 0
    dan15 = 0
    for index, item in incomes.iterrows():
        if item["mesic"] == int(numMonth) and item["rok"] == int(year):
            if not pd.isna(item["dic"]):
                obrat = obrat + item["castka_bez_dph"]
                dan = dan + item["dph"]
                A4 = et.SubElement(root.find("DPHKH1"), 'VetaA4')
                A4.set('c_radku', str(num))
                A4.set('dic_odb', str(int(item["dic"])))
                A4.set('c_evid_dd', str(item["cisloDokladu"]))
                A4.set('dppd', str(item["duzp"].strftime("%d.%m.%Y")))
                A4.set('zakl_dane1', str(round(item["castka_bez_dph"])))
                A4.set('dan1', str(round(item["dph"])))
                A4.set('kod_rezim_pl', '0')
                A4.set('zdph_44', 'N')
                num = num + 1
            else:
                obrat15 = obrat15 + item["castka_bez_dph"]
                dan15 = dan15 + item["dph"]
    A5 = et.SubElement(root.find("DPHKH1"), 'VetaA5')
    A5.set('zakl_dane2', str(round(obrat15)))
    A5.set('dan2', str(round(dan15)))

    # Expenses
    # VetaB3+B2
    dan_21 = 0
    zaklad_dane_21 = 0
    numB2 = 1
    dan_snizena = 0
    zakl_dane_snizena = 0
    for index, item in expenses.iterrows():
        if item["mesic"] == int(numMonth) and item["rok"] == int(year):
            castka_bez_dph = item["castka_bez_dph"]
            castka_celkem = item['castka_celkem']
            dan = item["dan"]
            dph = item["dph"]

            if castka_celkem < 10000 and dan == 21:
                zaklad_dane_21 = zaklad_dane_21 + castka_bez_dph
                dan_21 = dan_21 + dph
            elif castka_celkem < 10000 and (dan == 10 or dan == 15):
                zakl_dane_snizena = + castka_bez_dph
                dan_snizena = + dph
            elif castka_celkem >= 10000:
                if dan == 21:
                    B2 = et.SubElement(root.find("DPHKH1"), 'VetaB2')
                    B2.set('c_radku', str(numB2))
                    B2.set('dic_dod', str(item["dic"]))
                    B2.set('c_evid_dd', str(item["cisloDokladu"]))
                    B2.set('dppd', str(item["duzp"].strftime("%d.%m.%Y")))
                    B2.set('zakl_dane1', str(round(item["castka_bez_dph"])))
                    B2.set(str(round(item["dph"])))
                    B2.set('pomer', 'N')
                    B2.set('zdph_44', 'N')
                    numB2 = + numB2
                elif dan == 10 or dan == 15:
                    logging.warning(
                        'Setting VetaB2 - zaklad dane je vice jak 10000 a zaroven dan 10 nebo 15, neumim spravne vytvorit VetuB2')
                    raise ValueError(
                        'Setting VetaB2 - zaklad dane je vice jak 10000 a zaroven dan 10 nebo 15, neumim spravne vytvorit VetuB2')
                else:
                    continue

            else:
                continue
    B3 = et.SubElement(root.find("DPHKH1"), 'VetaB3')
    B3.set('zakl_dane1', str(round(zaklad_dane_21)))
    B3.set('dan1', str(round(dan_21)))
    B3.set('zakl_dane3', str(zakl_dane_snizena))
    B3.set('dan3', str(dan_snizena))

    # VetaC
    C = et.SubElement(root.find("DPHKH1"), 'VetaC')
    C.set('obrat23', str(round(obrat)))
    C.set('pln23', str(round(zaklad_dane_21)))
    C.set('pln5', str(zakl_dane_snizena))

    file_name = "kh_output.xml"
    head = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
    completeName = os.path.join(khOutputLoc, file_name)

    ktData = et.tostring(root)

    with open(completeName, "w") as f:
        f.write(head)
        f.write(str(ktData.decode("utf-8")))
