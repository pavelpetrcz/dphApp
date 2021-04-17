import PySimpleGUI as Sg

import dphFlow

# const
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
    layout = [
        [Sg.Text("Vyberte šablonu, měsíc, rok a cílové umístění XMLka.")],
        [Sg.Text("Vyber mesic a rok"), Sg.Combo(
            ['leden', 'unor', 'brezen', 'duben', 'kveten', 'cerven', 'cervenec', 'srpen', 'zari', 'rijen', 'listopad',
             'prosinec'], default_value="brezen", enable_events=True, key='combo_month')],
        [Sg.Text("Vyber rok"),
         Sg.Combo(["2021", "2022", "2023"], default_value="2021", enable_events=True, key='combo_year')],
        [Sg.Button("Calculate")]]

    # Create the window
    window = Sg.Window("DPH&KH", layout, size=(300, 170))

    # Create an event loop
    while True:
        event, values = window.read()
        # End program if user closes window or
        # presses the OK button
        if event == "Calculate":
            m = values["combo_month"]
            nm = month[m]
            y = values["combo_year"]
            dphFlow.execute(nm, y)

        elif event == Sg.WIN_CLOSED:
            break

    window.close()
