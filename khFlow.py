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

    # VetaA4
    num = 1
    obrat = 0
    dan = 0
    for index, item in incomes.iterrows():
        if item["mesic"] == int(numMonth) and item["rok"] == int(year):
            obrat = obrat + item["castka_bez_dph"]
            dan = dan + item["dph"]
            A4 = et.SubElement(root.find("DPHKH1"), 'VetaA4')
            A4.set('c_radku', str(num))
            A4.set('dic_odb', str(item["dic"]))
            A4.set('c_evid_dd', str(item["cisloDokladu"]))
            A4.set('dppd', str(item["duzp"].strftime("%d.%m.%Y")))
            A4.set('zakl_dane1', str(round(item["castka_bez_dph"])))
            A4.set('dan1', str(round(item["dph"])))
            A4.set('kod_rezim_pl', '0')
            A4.set('zdph_44', 'N')
            num = num + 1

    # VetaB3
    dan_21 = 0
    zaklad_dane_21 = 0
    for index, item in expenses.iterrows():
        if item["mesic"] == int(numMonth) and item["rok"] == int(year):
            castka = item["castka_bez_dph"]
            dan = item["dan"]
            dph = item["dph"]
            if castka < 10000 and dan == 21:
                zaklad_dane_21 = zaklad_dane_21 + castka
                dan_21 = dan_21 + dph
            elif castka < 10000 and (dan == 10 or dan == 15):
                zakl_dane_snizena = + castka
                dan_snizena = + dph

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
