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
    # VetaD (datum vystavení - d_poddp)
    datum_podani = commonMethods.getTodayDateAsString()

    DPHKH1.find("VetaD").set("mesic", str(numMonth))
    DPHKH1.find("VetaD").set("rok", str(year))
    DPHKH1.find("VetaD").set("d_poddp", datum_podani)

    # Incomes
    # VetaA4+A5
    in_row_number = 1
    in_castka_bez_dph21 = 0
    in_castka_dph21 = 0
    in_castka_bez_dph_15 = 0
    in_castka_dph15 = 0
    for index, item in incomes.iterrows():
        if item["mesic"] == int(numMonth) and item["rok"] == int(year):
            if not pd.isna(item["dic"]):
                in_castka_bez_dph21 = in_castka_bez_dph21 + item["castka_bez_dph"]
                in_castka_dph21 = in_castka_dph21 + item["dph"]
                A4 = et.SubElement(root.find("DPHKH1"), 'VetaA4')
                A4.set('c_radku', str(in_row_number))
                A4.set('dic_odb', str(int(item["dic"])))
                A4.set('c_evid_dd', str(item["cisloDokladu"]))
                A4.set('dppd', str(item["duzp"].strftime("%d.%m.%Y")))
                A4.set('zakl_dane1', str(round(item["castka_bez_dph"])))
                A4.set('dan1', str(round(item["dph"])))
                A4.set('kod_rezim_pl', '0')
                A4.set('zdph_44', 'N')
                in_row_number = in_row_number + 1
            else:
                in_castka_bez_dph_15 = in_castka_bez_dph_15 + item["castka_bez_dph"]
                in_castka_dph15 = in_castka_dph15 + item["dph"]
    A5 = et.SubElement(root.find("DPHKH1"), 'VetaA5')
    A5.set('zakl_dane2', str(round(in_castka_bez_dph_15)))
    A5.set('dan2', str(round(in_castka_dph15)))

    # Expenses
    # VetaB3+B2
    numB2 = 1

    ex_dph_celkem_21 = 0
    ex_castka_bez_dph_celkem_21 = 0

    ex_dph_celkem_15 = 0
    ex_castka_bez_dph_celkem_15 = 0

    ex_dph_celkem_10 = 0
    ex_castka_bez_dph_celkem_10 = 0

    for index, item in expenses.iterrows():
        if item["mesic"] == int(numMonth) and item["rok"] == int(year):
            ex_castka_bez_dph = item["castka_bez_dph"]
            ex_castka_celkem = item['castka_celkem']
            ex_sazba = item["sazba"]
            ex_castka_dph = item["dph"]

            if ex_castka_celkem < 10000 and ex_sazba == 21:
                ex_castka_bez_dph_celkem_21 = ex_castka_bez_dph_celkem_21 + ex_castka_bez_dph
                ex_dph_celkem_21 = ex_dph_celkem_21 + ex_castka_dph
            elif ex_castka_celkem < 10000 and ex_sazba == 15:
                ex_castka_bez_dph_celkem_15 = + ex_castka_bez_dph
                ex_dph_celkem_15 = + ex_castka_dph
            elif ex_castka_celkem < 10000 and ex_sazba == 10:
                ex_castka_bez_dph_celkem_10 = + ex_castka_bez_dph
                ex_dph_celkem_10 = + ex_castka_dph
            elif ex_castka_celkem >= 10000:
                if ex_sazba == 21:
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
                elif ex_sazba == 10 or ex_sazba == 15:
                    logging.warning(
                        'Setting VetaB2 - zaklad dane je vice jak 10000 a zaroven dan 10 nebo 15, neumim spravne vytvorit VetuB2')
                    raise ValueError(
                        'Setting VetaB2 - zaklad dane je vice jak 10000 a zaroven dan 10 nebo 15, neumim spravne vytvorit VetuB2')
                else:
                    continue

            else:
                continue
    B3 = et.SubElement(root.find("DPHKH1"), 'VetaB3')
    B3.set('zakl_dane1', str(round(ex_castka_bez_dph_celkem_21)))
    B3.set('dan1', str(round(ex_dph_celkem_21)))
    B3.set('zakl_dane3', str(ex_castka_bez_dph_celkem_10))
    B3.set('dan3', str(ex_dph_celkem_10))
    B3.set('dan2', str(round(ex_dph_celkem_15)))
    B3.set('zakl_dane2', str(round(ex_castka_bez_dph_celkem_15)))

    # VetaC
    C = et.SubElement(root.find("DPHKH1"), 'VetaC')
    C.set('obrat23', str(round(in_castka_bez_dph21)))
    C.set('pln23', str(round(ex_castka_bez_dph_celkem_21)))
    C.set('pln5', str(ex_castka_bez_dph_celkem_15 + ex_castka_bez_dph_celkem_10))

    file_name = "kh_output.xml"
    head = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
    completeName = os.path.join(khOutputLoc, file_name)

    khData = et.tostring(root)

    with open(completeName, "w") as f:
        f.write(head)
        f.write(str(khData.decode("utf-8")))
