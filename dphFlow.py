import lxml.etree as et
from datetime import date
import pandas as pd


def execute():
    tree = et.parse('template_dph.xml')
    root = tree.getroot()
    DPHDP3 = root.find("DPHDP3")

    # print(et.tostring(root, pretty_print=True).decode("utf-8"))

    # Vypočet
    month = int(input("Měsíc: "))  # zadám měsíc
    year = int(input("Rok: "))  # zadám rok

    prijmy = pd.read_excel("A://OSVC//dph//evidence.xlsx", sheet_name="prijmy")
    vydaje = pd.read_excel("A://OSVC//dph//evidence.xlsx", sheet_name="vydaje")

    # načtu zdrojova data
    # dan na vstupu
    # ve vydajich najdu odpovídající měsic a rok a spočtu součet
    vyd_sum_cbd = 0
    vyd_sum_dph = 0
    for index, item in vydaje.iterrows():
        if item["mesic"] == month and item["rok"] == year:
            vyd_sum_cbd += item["castka_bez_dph"]
            vyd_sum_dph += item["dph"]

    # dan na vystupu
    prij_sum_cbd = 0
    prij_sum_dph = 0
    for index, item in prijmy.iterrows():
        if item["mesic"] == month and item["rok"] == year:
            prij_sum_cbd += item["castka_bez_dph"]
            prij_sum_dph += item["dph"]

    # Co měnit v XMLku
    # VetaD
    # - mesic - mesic
    # - rok - rok
    # - datum vystavení - d_poddp
    today = date.today()
    datum_podani = today.strftime("%d.%m.%Y")

    DPHDP3.find("VetaD").set("mesic", str(month))
    DPHDP3.find("VetaD").set("rok", str(year))
    DPHDP3.find("VetaD").set("d_poddp", datum_podani)

    # Veta1
    # - dan na vystupu - dan23
    # - zaklad na vystupu - obrat23
    DPHDP3.find("Veta1").set("dan23", str(round(prij_sum_dph)))
    DPHDP3.find("Veta1").set("obrat23", str(round(prij_sum_cbd)))

    # Veta4
    # - součtový řádek - odp_sum_nar
    # - dan na vstupu - odp_tuz23_nar
    # - castka bez dph na vstupu - pln23
    DPHDP3.find("Veta4").set("pln23", str(round(vyd_sum_cbd)))
    DPHDP3.find("Veta4").set("odp_tuz23_nar", str(round(vyd_sum_dph)))
    DPHDP3.find("Veta4").set("odp_sum_nar", str(round(vyd_sum_dph)))

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

    print(et.tostring(root).decode("utf-8"))

    mydata = et.tostring(root)
    head = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"

    with open("items2.xml", "w") as f:
        f.write(head)
        f.write(str(mydata.decode("utf-8")))
