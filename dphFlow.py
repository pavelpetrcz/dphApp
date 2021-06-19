import os

import lxml.etree as et
import pandas as pd

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

    # print(et.tostring(root, pretty_print=True).decode("utf-8"))

    # load source data
    incomes = pd.read_excel("A://OSVC//dph//evidence.xlsx", sheet_name="prijmy", engine='openpyxl')
    expenses = pd.read_excel("A://OSVC//dph//evidence.xlsx", sheet_name="vydaje", engine='openpyxl')

    # dan na vstupu
    # ve vydajich najdu odpovídající měsic a rok a spočtu součet
    vyd_sum_cbd = 0
    vyd_sum_dph = 0
    vyd_sum_cbd10 = 0
    vyd_sum_dph10 = 0

    for index, item in expenses.iterrows():
        if item["mesic"] == int(month) and item["rok"] == int(year):
            if item["dan"] == 21:
                vyd_sum_cbd = vyd_sum_cbd + item["castka_bez_dph"]
                vyd_sum_dph = vyd_sum_dph + item["dph"]
            elif item["dan"] == 10:
                vyd_sum_cbd10 = vyd_sum_cbd10 + item["castka_bez_dph"]
                vyd_sum_dph10 = vyd_sum_dph10 + item["dph"]

    # dan na vystupu
    prij_sum_cbd = 0
    prij_sum_dph = 0
    for index, item in incomes.iterrows():
        if item["mesic"] == int(month) and item["rok"] == int(year):
            prij_sum_cbd += item["castka_bez_dph"]
            prij_sum_dph += item["dph"]

    # Co měnit v XMLku
    # VetaD
    # - mesic - mesic
    # - rok - rok
    # - datum vystavení - d_poddp
    datum_podani = commonMethods.getTodayDateAsString()

    DPHDP3.find("VetaD").set("mesic", str(month))
    DPHDP3.find("VetaD").set("rok", str(year))
    DPHDP3.find("VetaD").set("d_poddp", datum_podani)

    # Veta1
    # - dan na vystupu - dan23
    # - zaklad na vystupu - obrat23
    DPHDP3.find("Veta1").set("dan23", str(round(prij_sum_dph)))
    DPHDP3.find("Veta1").set("obrat23", str(round(prij_sum_cbd)))

    # Veta4
    # 21%
    # součtový řádek - odp_sum_nar, dan na vstupu - odp_tuz23_nar, castka bez dph na vstupu - pln23
    DPHDP3.find("Veta4").set("pln23", str(round(vyd_sum_cbd)))
    DPHDP3.find("Veta4").set("odp_tuz23_nar", str(round(vyd_sum_dph)))
    DPHDP3.find("Veta4").set("odp_sum_nar", str(round(vyd_sum_dph)))

    # 10%
    DPHDP3.find("Veta4").set("odp_sum_nar", str(round(vyd_sum_dph10 + vyd_sum_cbd10)))
    DPHDP3.find("Veta4").set("odp_tuz23_nar", str(round(vyd_sum_cbd10)))
    DPHDP3.find("Veta4").set("odp_tuz5_nar", str(round(vyd_sum_dph10)))

    # Veta6
    # - celkova dan vystupu - dan_zocelk
    # - rozdil dani na vstupu a vystupu - dano_da / dano_no - da -> když na vystup je vysi nez na vstupu, pokud jinak -> no
    # - celkova dan na vstupu - odp_zocelk
    DPHDP3.find("Veta6").set("dan_zocelk", str(round(prij_sum_dph)))
    DPHDP3.find("Veta6").set("odp_zocelk", str(round(vyd_sum_dph)))

    vysledek = prij_sum_dph - vyd_sum_dph

    if vysledek > 0:
        DPHDP3.find("Veta6").set("dano_da", str(abs(round(vysledek))))
    else:
        DPHDP3.find("Veta6").set("dano_no", str(abs(round(vysledek))))

    # print(et.tostring(root).decode("utf-8"))
    mydata = et.tostring(root)
    head = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"

    file_name = "dph_output.xml"

    completeName = os.path.join(dphOutputLoc, file_name)

    with open(completeName, "w") as f:
        f.write(head)
        f.write(str(mydata.decode("utf-8")))
