import os
import lxml.etree as et
import pandas as pd
import logging

import commonMethods


def execute(month, year, dphOutputLoc, dphTempFile):
    """

    :param month: numeric value of month (1-12)
    :param year: numeric value of year (2021)
    :param dphOutputLoc: where to save final XML file
    :param dphTempFile: templete to override
    """
    tree = et.parse(dphTempFile)
    root = tree.getroot()
    DPHDP3 = root.find("DPHDP3")

    # load source data
    incomes = pd.read_excel("A://OSVC//dph//evidence.xlsx", sheet_name="prijmy", engine='openpyxl')
    expenses = pd.read_excel("A://OSVC//dph//evidence.xlsx", sheet_name="vydaje", engine='openpyxl')

    # dan na vstupu
    vyd_sum_cbd = 0
    vyd_sum_dph = 0
    vyd_sum_cbd_snizena = 0
    vyd_sum_dph_snizena = 0

    for index, item in expenses.iterrows():
        if item["mesic"] == int(month) and item["rok"] == int(year):
            if item["sazba"] == 21:
                vyd_sum_cbd = vyd_sum_cbd + item["castka_bez_dph"]
                vyd_sum_dph = vyd_sum_dph + item["dph"]
            elif item["sazba"] == 10 or item["sazba"] == 15:
                vyd_sum_cbd_snizena = vyd_sum_cbd_snizena + item["castka_bez_dph"]
                vyd_sum_dph_snizena = vyd_sum_dph_snizena + item["dph"]

    # dan na vystupu
    prij_sum_cbd = 0
    prij_sum_dph = 0
    prij_sum_cbd_15 = 0
    prij_sum_dph_15 = 0
    for index, item in incomes.iterrows():
        if item["mesic"] == int(month) and item["rok"] == int(year):
            if item["sazba"] == 21:
                prij_sum_cbd += item["castka_bez_dph"]
                prij_sum_dph += item["dph"]
            elif item["sazba"] == 15:
                prij_sum_cbd_15 += item["castka_bez_dph"]
                prij_sum_dph_15 += item["dph"]
            else:
                logging.warning("Snizena sazba 10% na vystupu.")
                raise Exception("Pozor - snizena sazba 10% na vystupu.")

    # VetaD
    # - datum vystavení - d_poddp
    datum_podani = commonMethods.getTodayDateAsString()

    DPHDP3.find("VetaD").set("mesic", str(month))
    DPHDP3.find("VetaD").set("rok", str(year))
    DPHDP3.find("VetaD").set("d_poddp", datum_podani)

    # Veta1
    # 21%
    # - dan na vystupu - dan23
    # - zaklad na vystupu - obrat23
    DPHDP3.find("Veta1").set("dan23", str(round(prij_sum_dph)))
    DPHDP3.find("Veta1").set("obrat23", str(round(prij_sum_cbd)))

    # 15%
    DPHDP3.find("Veta1").set("dan5", str(round(prij_sum_dph_15)))
    DPHDP3.find("Veta1").set("obrat5", str(round(prij_sum_cbd_15)))

    # Veta4
    # 21%
    # součtový řádek - odp_sum_nar, dan na vstupu - odp_tuz23_nar, castka bez dph na vstupu - pln23
    DPHDP3.find("Veta4").set("pln23", str(round(vyd_sum_cbd)))
    DPHDP3.find("Veta4").set("odp_tuz23_nar", str(round(vyd_sum_dph)))
    # DPHDP3.find("Veta4").set("odp_sum_nar", str(round(vyd_sum_dph)))

    # snizena sazba (10 % a 15%)
    DPHDP3.find("Veta4").set("pln5", str(round(vyd_sum_cbd_snizena)))
    DPHDP3.find("Veta4").set("odp_tuz5_nar", str(round(vyd_sum_dph_snizena)))
    # soucet
    DPHDP3.find("Veta4").set("odp_sum_nar", str(round(vyd_sum_dph_snizena + vyd_sum_dph)))

    # Veta6
    # - celkova dan vystupu - dan_zocelk
    # - rozdil dani na vstupu a vystupu - dano_da / dano_no - da -> když na vystup je vysi nez na vstupu, pokud jinak -> no
    # - celkova dan na vstupu - odp_zocelk
    DPHDP3.find("Veta6").set("dan_zocelk", str(round(prij_sum_dph + prij_sum_dph_15)))
    DPHDP3.find("Veta6").set("odp_zocelk", str(round(vyd_sum_dph + vyd_sum_dph_snizena)))

    vysledek = prij_sum_dph + prij_sum_dph_15 - vyd_sum_dph - vyd_sum_dph_snizena

    if vysledek > 0:
        DPHDP3.find("Veta6").set("dano_da", str(abs(round(vysledek))))
    else:
        DPHDP3.find("Veta6").set("dano_no", str(abs(round(vysledek))))

    mydata = et.tostring(root)
    head = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"

    file_name = "dph_output.xml"

    completeName = os.path.join(dphOutputLoc, file_name)

    with open(completeName, "w") as f:
        f.write(head)
        f.write(str(mydata.decode("utf-8")))
