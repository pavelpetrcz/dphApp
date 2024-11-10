import time
import PySimpleGUI as Sg

import dphFlow
import khFlow
import commonMethods as Cm

# constants
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


def display_main_window():
    dph_temp_loc = "C:/Users/pavel/Desktop/template_dph.xml"
    default_output_loc = 'C:\\Users\\pavel\\Desktop\\'
    kt_temp_loc = "C:/Users/pavel/Desktop/template_kh.xml"

    def get_month_and_year():
        """
        convert strings to numerical records
        :return: dict with choosen month and year
        """
        nm = month[values["combo_month"]]
        y = values["combo_year"]
        result = {"nm": nm, "y": y}
        return result

    def get_name_of_previous_month():
        """
        get name of actual month
        :return: czech name of actual month
        """
        actual_month = int(time.strftime("%m"))
        # minus two to fix offset in list and set previous; if month is 1
        am = actual_month + 10 if actual_month == 1 else actual_month - 2
        key_list = list(month.keys())
        return key_list[am]

    tab1_layout = [

        [Sg.Text("Vyberte XML šablonu a umístění výstupu:")],
        [Sg.Text('Šablona:', size=(7, 1)), Sg.InputText(default_text=dph_temp_loc),
         Sg.FileBrowse(key='dphtempFile', file_types=(("XML Files", "*.xml"),),
                       initial_folder='C:\\Users\\pavel\\Desktop\\')],
        [Sg.Text('Výstupní složka:', size=(12, 1)), Sg.InputText(default_text='C:\\Users\\pavel\\Desktop\\'),
         Sg.FolderBrowse(key='dph_temp_loc')],
        [Sg.Button("Generuj DPH", button_color='red')]
    ]

    tab2_layout = [
        [Sg.Text("Vyberte XML šablonu a umístění výstupu:")],
        [Sg.Text('Šablona:', size=(7, 1)), Sg.InputText(default_text=kt_temp_loc),
         Sg.FileBrowse(key='khTempFile', file_types=(("XML Files", "*.xml"),),
                       initial_folder='C:\\Users\\pavel\\Desktop\\')],
        [Sg.Text('Výstupní složka:', size=(12, 1)), Sg.InputText(default_text='C:\\Users\\pavel\\Desktop\\'),
         Sg.FolderBrowse(key='ktTempLoc')],
        [Sg.Button("Generuj KH", button_color='red')]
    ]

    layout = [
        [Sg.Text("Vyberte měsíc a rok")],
        [Sg.Combo(
            ['leden', 'unor', 'brezen', 'duben', 'kveten', 'cerven', 'cervenec', 'srpen', 'zari', 'rijen', 'listopad',
             'prosinec'], default_value=get_name_of_previous_month(), enable_events=True, key='combo_month'),
            Sg.Combo(["2021", "2022", "2023", "2024", "2025", "2026", "2027", "2028", "2029", "2030"], default_value=Cm.getThisYear(), enable_events=True, key='combo_year')],
        [Sg.Text()],
        [Sg.Frame('Dan z pridane hodnoty', tab1_layout, font='Any 12', title_color='white')],
        [Sg.Frame('Kontrolni hlaseni', tab2_layout, font='Any 12', title_color='white')]
    ]

    # Create the window
    window = Sg.Window("DPH & Kontrolní hlaseni", layout, size=(550, 400), icon='resource/receipt_tax_icon.ico')

    # Create an event loop
    while True:
        event, values = window.read()
        data = get_month_and_year()
        # End program if user closes window or
        # presses the OK button
        if event == "Generuj DPH":
            dph_loc = values["dph_temp_loc"] if values["dph_temp_loc"] != "" else dph_temp_loc
            dphFlow.execute(data["nm"], data["y"], default_output_loc, dph_loc)

        elif event == "Generuj KH":
            try:
                khloc = values["khTempFile"] if values["khTempFile"] != "" else kt_temp_loc
                khFlow.execute(data["nm"], data["y"], default_output_loc, khloc)
            except ValueError as e:
                Sg.popup_error(e, title='Chyba', modal=True)

        elif event == Sg.WIN_CLOSED:
            break

    window.close()
