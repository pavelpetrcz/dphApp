import PySimpleGUI as Sg
from datetime import date

import dphFlow

# const
import khFlow

month = {
    "leden": "1",
    "unor": "2",
    "brezen": "3",
    "duben": "4",
    "kveten": "5",
    "cerven": "6",
    "cervenec": "7",
    "srpen": "8",
    "zari": "9",
    "rijen": "10",
    "listopad": "11",
    "prosinec": "12"
}


def displayMainWindow():
    dphTempLoc = "C:/Users/pavel/Desktop/template_dph.xml"
    defaultOutputLoc = 'C:\\Users\\pavel\\Desktop\\'
    ktTempLoc = "C:/Users/pavel/Desktop/template_kh.xml"

    def getMonthAndYear():
        nm = month[values["combo_month"]]
        y = values["combo_year"]
        result = {"nm": nm, "y": y}
        return result

    month_key = date.month
    print(month_key)



    tab1_layout = [

        [Sg.Text("Vyberte XML šablonu a umístění výstupu:")],
        [Sg.Text('Šablona:', size=(7, 1)), Sg.InputText(default_text=dphTempLoc),
         Sg.FileBrowse(key='dphtempFile', file_types=(("XML Files", "*.xml"),),
                       initial_folder='C:\\Users\\pavel\\Desktop\\')],
        [Sg.Text('Výstupní složka:', size=(12, 1)), Sg.InputText(default_text='C:\\Users\\pavel\\Desktop\\'), Sg.FolderBrowse(key='dphTempLoc')],
        [Sg.Button("Generuj DPH", button_color='red')]
    ]

    tab2_layout = [
        [Sg.Text("Vyberte XML šablonu a umístění výstupu:")],
        [Sg.Text('Šablona:', size=(7, 1)), Sg.InputText(default_text=ktTempLoc),
         Sg.FileBrowse(key='khTempFile', file_types=(("XML Files", "*.xml"),),
                       initial_folder='C:\\Users\\pavel\\Desktop\\')],
        [Sg.Text('Výstupní složka:', size=(12, 1)), Sg.InputText(default_text='C:\\Users\\pavel\\Desktop\\'), Sg.FolderBrowse(key='ktTempLoc')],
        [Sg.Button("Generuj KH", button_color='red')]
    ]

    layout = [
        [Sg.Text("Vyberte měsíc a rok")],
        [Sg.Combo(
            ['leden', 'unor', 'brezen', 'duben', 'kveten', 'cerven', 'cervenec', 'srpen', 'zari', 'rijen', 'listopad',
             'prosinec'], default_value="brezen", enable_events=True, key='combo_month'),
            Sg.Combo(["2021", "2022", "2023"], default_value="2021", enable_events=True, key='combo_year')],
        [Sg.Text()],
        [Sg.Frame('Dan z pridane hodnoty', tab1_layout, font='Any 12', title_color='white')],
        [Sg.Frame('Kontrolni hlaseni', tab2_layout, font='Any 12', title_color='white')]
    ]

    # Create the window
    window = Sg.Window("DPH & Kontrolní hlaseni", layout, size=(550, 400), icon='resource/receipt_tax_icon.ico')

    # Create an event loop
    while True:
        event, values = window.read()
        data = getMonthAndYear()
        # End program if user closes window or
        # presses the OK button
        if event == "Generuj DPH":
            dphLoc = values["dphTempLoc"] if values["dphTempLoc"] != "" else dphTempLoc
            dphFlow.execute(data["nm"], data["y"], defaultOutputLoc, dphLoc)

        elif event == "Generuj KH":
            khloc = values["khTempFile"] if values["khTempFile"] != "" else ktTempLoc
            khFlow.execute(data["nm"], data["y"], defaultOutputLoc, khloc)

        elif event == Sg.WIN_CLOSED:
            break

    window.close()
