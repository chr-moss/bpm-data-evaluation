
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd

# ========================================================
# Funktionen zur Erstellung der Plots
# ========================================================

def voltage_number(hold_voltage):
    return f"{hold_voltage:.2f}".rstrip("0").rstrip(".") + "V"

def current_number(hold_current):
    if hold_current < 1:
        hold_current_ma = hold_current * 1000
        return f"{hold_current_ma:.1f}".rstrip("0").rstrip(".") + "mA"
    else:
        return f"{hold_current:.2f}".rstrip("0").rstrip(".") + "A"

def peis_nyquist(real_impedance: pd.Series, imaginary_impedance: pd.Series, hold_voltage, step, show_plot: bool, loop1, output_dir: Path, file_path, cleaned: bool):
     step_label = step.replace("task_", "step_")
     voltage_label = voltage_number(hold_voltage)
     plt.figure(figsize=[6.4*1.3,4.8*1.3])
     plt.plot(real_impedance, imaginary_impedance, marker = "o", label = f"Step {step_label} - PEIS at {voltage_label}")
     plt.legend()
     plt.xlabel("Re / Ohm", fontsize = 14, labelpad = 10)
     plt.ylabel("-Im / Ohm", fontsize = 14, labelpad = 8)
     plt.grid(True, alpha=0.3)

     if cleaned:
         folder_name = "Nyquist_Plots_cleaned"
         suffix = "PEIS_cl"
     else:
         folder_name = "Nyquist_Plots"
         suffix = "PEIS"

     if pd.isna(loop1) or loop1 == "":
         plot_dir = output_dir / folder_name
         plot_dir.mkdir(parents=True, exist_ok=True)
         plot_path = plot_dir / f"{file_path.stem}_{suffix}.png"
     else:
         plot_dir = output_dir / folder_name / f"Loop_{loop1:.0f}"
         plot_dir.mkdir(parents=True, exist_ok=True)
         plot_path = plot_dir / f"{file_path.stem}_{step_label}_{loop1:.0f}_{suffix}.png"

     # plt.tight_layout() -> nicht verwendet, da ohne padding nicht mehr symmetrisch
     plt.savefig(plot_path , dpi = 300)
     if show_plot:
         plt.show()
     plt.close()

def geis_nyquist(real_impedance: pd.Series, imaginary_impedance: pd.Series, hold_voltage, step,
                 show_plot: bool, loop1, output_dir: Path, file_path, cleaned: bool):
    step_label = step.replace("task_", "step_")
    current_label = current_number(hold_voltage)
    plt.figure(figsize=[6.4 * 1.3, 4.8 * 1.3])
    plt.plot(real_impedance, imaginary_impedance, marker="o", label=f"Step {step_label} - GEIS at {current_label}")
    plt.legend()
    plt.xlabel("Re / Ohm", fontsize=14, labelpad=10)
    plt.ylabel("-Im / Ohm", fontsize=14, labelpad=8)
    plt.grid(True, alpha=0.3)

    if cleaned:
        folder_name = "Nyquist_Plots_cleaned"
        suffix = "GEIS_cl"
    else:
        folder_name = "Nyquist_Plots"
        suffix = "GEIS"

    if pd.isna(loop1) or loop1 == "":
        plot_dir = output_dir / folder_name
        plot_dir.mkdir(parents=True, exist_ok=True)
        plot_path = plot_dir / f"{file_path.stem}_{suffix}.png"
    else:
        plot_dir = output_dir / folder_name / f"Loop_{loop1:.0f}"
        plot_dir.mkdir(parents=True, exist_ok=True)
        plot_path = plot_dir / f"{file_path.stem}_{step_label}_{loop1:.0f}_{suffix}.png"

    # plt.tight_layout() -> nicht verwendet, da ohne padding nicht mehr symmetrisch
    plt.savefig(plot_path, dpi=300)
    if show_plot:
        plt.show()
    plt.close()

def hfr_plot(output_dir, task, loop1, hfr_estimates,hold_currents,starting_voltage,ending_voltage,
                  starting_current, ending_current, curve_number, show_plot):
    if task == "PEIS":
        plot_label = f"HFR Curve {curve_number} {voltage_number(starting_voltage)}-{voltage_number(ending_voltage)}"
    else:
        plot_label = f"HFR Curve {curve_number} {current_number(starting_current)}-{current_number(ending_current)}"
    plt.figure(figsize=[6.4*1.3,4.8*1.3])
    plt.plot(hold_currents, hfr_estimates, marker="o", label = plot_label)
    plt.legend()
    plt.xlabel("I / A", fontsize = 14, labelpad = 10)
    plt.ylabel("HFR / Ohm", fontsize = 14, labelpad = 8)
    plt.grid(True, alpha=0.3)
    if pd.isna(loop1) or loop1 == "":
        plot_dir = output_dir / "ui_curves"
        plot_dir.mkdir(parents=True, exist_ok=True)
        plot_path = plot_dir / f"{curve_number}_{task}_HFR.png"
    else:
        plot_dir = output_dir / "ui_curves" / f"Loop_{loop1:.0f}"
        plot_dir.mkdir(parents=True, exist_ok=True)
        plot_path = plot_dir / f"{curve_number}_{task}_{loop1:.0f}_HFR.png"
    # plt.tight_layout() -> nicht verwendet, da ohne padding nicht mehr symmetrisch
    plt.savefig(plot_path , dpi = 300)
    if show_plot:
        plt.show()
    plt.close()


def ui_curve_plot(output_dir, task, loop1, hold_voltages,hold_currents,starting_voltage,ending_voltage,
                  starting_current, ending_current, curve_number, show_plot):
    if task == "PEIS":
        plot_label = f"U/I Curve {curve_number} {voltage_number(starting_voltage)}-{voltage_number(ending_voltage)}"
    else:
        plot_label = f"U/I Curve {curve_number} {current_number(starting_current)}-{current_number(ending_current)}"
    plt.figure(figsize=[6.4*1.3,4.8*1.3])
    plt.plot(hold_currents, hold_voltages, marker="o", label = plot_label)
    plt.legend()
    plt.xlabel("I / A", fontsize = 14, labelpad = 10)
    plt.ylabel("U / V", fontsize = 14, labelpad = 8)
    plt.grid(True, alpha=0.3)
    if pd.isna(loop1) or loop1 == "":
        plot_dir = output_dir / "ui_curves"
        plot_dir.mkdir(parents=True, exist_ok=True)
        plot_path = plot_dir / f"{curve_number}_{task}_UI.png"
    else:
        plot_dir = output_dir / "ui_curves" / f"Loop_{loop1:.0f}"
        plot_dir.mkdir(parents=True, exist_ok=True)
        plot_path = plot_dir / f"{curve_number}_{task}_{loop1:.0f}_UI.png"
    # plt.tight_layout() -> nicht verwendet, da ohne padding nicht mehr symmetrisch
    plt.savefig(plot_path , dpi = 300)
    if show_plot:
        plt.show()
    plt.close()


# ========================================================
# Hauptfunktion Start
# ========================================================

def evaluate(input_folder: Path, output_folder: Path, eis_hold_values, show_plot):

    # ========================================================
    # Container für Dokumentation
    # ========================================================

    # Die Werte in den dicts sind anhand der measurement_id identifizierbar
    eis_results = {}

    # ========================================================
    # File Handling
    # ========================================================

    input_dir = Path(input_folder)
    if not input_dir.is_dir():
        exit("Input directory does not exist")

    # Output Ordner definieren

    output_dir = Path(output_folder)
    output_dir.mkdir(exist_ok=True)

    # File öffnen, Output Path kommt ggf. später dazu - Dataframe erstellen

    for original_file_path in input_dir.glob("*.csv"):
        df = pd.read_csv(original_file_path)

        file_path = original_file_path.with_stem(
            original_file_path.stem.removesuffix("_corrected")
        )

        # Measurement_id für Doku definieren
        measurement_id = (df["Step"].iloc[0], df["Task"].iloc[0], df["Loop 1 number"].iloc[0], df["Segment"].iloc[0])
        method = df["Task"].iloc[0]
        loop1 = df["Loop 1 number"].iloc[0] #brauchen wir für Aufteilung in Ordner
        loop_id = None if pd.isna(loop1) else loop1
        segment = df["Segment"].iloc[0]

        if method not in ["PEIS", "GEIS"] or segment != "eis":
            continue

        # ========================================================
        # df und Series erzeugen
        # ========================================================

        eis_df = df[
            df["Frequency /Hz"].notna()
            & df["Real impedance /Ohms"].notna()
            & df["- Imaginary impedance /Ohms"].notna()
            ].sort_values("Frequency /Hz", ascending=False).reset_index(drop=True)

        if eis_df.empty:
            eis_results[measurement_id] = {
                "Hold voltage": "n/a",
                "Hold current": "n/a",
                "EIS points": "n/a",
                "HFR estimate": "n/a",
                "HFR frequency": "n/a",
                "HFR -Imag": "n/a",
                "HF points used": "n/a",
                "HF cleaning points removed": "n/a",
                "evaluation_status": "no valid EIS data"
            }
            continue

        time = eis_df["Time /s"]
        step = eis_df["Step"].iloc[0]
        task = eis_df["Task"].iloc[0]
        voltage = eis_df["U /V"]
        current = eis_df["I /A"]
        frequency = eis_df["Frequency /Hz"]
        impedance_module = eis_df["Impedance module /Ohms"]
        impedance_phase = eis_df["Impedance phase /rad"]
        real_impedance = eis_df["Real impedance /Ohms"]
        imaginary_impedance = eis_df["- Imaginary impedance /Ohms"]

        hold_id = (step, task, loop_id, "hold")

        # ========================================================
        # Ermittlung des HFR und Vorbereitung HFR-Plot
        # ========================================================

        # only High-Frequency Region
        hf_fraction = 0.5
        n_hf = max(1, int(len(eis_df) * hf_fraction)) # der zweite Wert ist der Zielwert, max +1 sicher gegen 0 ab
        eis_hf = eis_df.head(n_hf) # schneidet sozusagen n_hf zeilen oben ab und speichert sie in eis_hf

        # smallest -Im finden, only positive -Im are valid
        hfr_candidates = eis_hf[eis_hf["- Imaginary impedance /Ohms"] > 0]

        if hfr_candidates.empty:
            eis_results[measurement_id] = {
                "Hold voltage": "n/a",
                "Hold current": "n/a",
                "EIS points": "n/a",
                "HFR estimate": "n/a",
                "HFR frequency": "n/a",
                "HFR -Imag": "n/a",
                "HF points used": "n/a",
                "HF cleaning points removed": "n/a",
                "evaluation_status": "no positive hfr"
            }
            continue
        else:
            hfr_index = hfr_candidates["- Imaginary impedance /Ohms"].idxmin() #Index des kleinsten Werts

            hfr_estimate = hfr_candidates.loc[hfr_index, "Real impedance /Ohms"] #df.loc holt Wert mit Index und Spaltenname
            hfr_frequency = hfr_candidates.loc[hfr_index, "Frequency /Hz"]
            hfr_minus_imag = hfr_candidates.loc[hfr_index, "- Imaginary impedance /Ohms"]

        # ========================================================
        # Hold-Values erzeugen
        # ========================================================

        hold_voltage = eis_hold_values[hold_id][0]
        hold_current = eis_hold_values[hold_id][1]

        # ========================================================
        # Nyquist Plots erstellen
        # ========================================================

        # Verweis zur Nyquist Funktion für raw Nyquist
        cleaned = False
        if task == "GEIS":
            geis_nyquist(real_impedance, imaginary_impedance, hold_current, step, show_plot, loop1, output_dir, file_path, cleaned)
        elif task == "PEIS":
            peis_nyquist(real_impedance, imaginary_impedance, hold_voltage, step, show_plot, loop1, output_dir, file_path, cleaned)


        # Clean - Points über HFR estimate entfernen
        eis_cleaned_df = eis_df.iloc[hfr_index:]
        hf_points_cleaned = len(eis_df) - len(eis_cleaned_df)

        real_impedance_cleaned = eis_cleaned_df["Real impedance /Ohms"]
        imaginary_impedance_cleaned = eis_cleaned_df["- Imaginary impedance /Ohms"]

        # Mit cleaned Datensatz wieder Nyquist Plot funktion aufrufen, entweder mit cleaned True/Fals oder eigene Funktion
        cleaned = True
        if task == "GEIS":
            geis_nyquist(real_impedance_cleaned, imaginary_impedance_cleaned, hold_current, step, show_plot, loop1,
                         output_dir, file_path, cleaned)
        elif task == "PEIS":
            peis_nyquist(real_impedance_cleaned, imaginary_impedance_cleaned, hold_voltage, step, show_plot, loop1,
                         output_dir, file_path, cleaned)


        # ========================================================
        # EIS Daten speichern
        # ========================================================

        eis_results[measurement_id] = {
            "Hold voltage": hold_voltage,
            "Hold current": hold_current,
            "EIS points": len(eis_df), # Zahl aller EIS Punkte
            "HFR estimate": hfr_estimate, # Re(Z) vom HFR Punkt
            "HFR frequency": hfr_frequency, # f vom HFR Punkt
            "HFR -Imag": hfr_minus_imag, # - Im vom HFR Punkt
            "HF points used": len(eis_hf), # Wie viele Punkte der HF-Teil sind
            "HF cleaning points removed": hf_points_cleaned,
            "evaluation_status": "ok"
        }


    # ========================================================
    # Results-Dict in Dataframe umwandeln
    # ========================================================

    result_rows = []

    for measurement_id, values in eis_results.items():
        step, task, loop1, segment = measurement_id #die Einzelnen Werte aus dem key holen

        row = {
            "Step": step,
            "Task": task,
            "Loop 1 number": loop1,
            "Segment": segment,
        }

        row.update(values) # übernimmt die values als neue Values in row (ein bisschen wie append aber größer)

        result_rows.append(row) # Es entsteht eine Liste von dicts -> die kann pandas direkt übernehmen

    eis_results_df = pd.DataFrame(result_rows)

    # Steps in reine Zahlen umwandeln und als Spalte anfügen
    eis_results_df["Step number"] = (
        eis_results_df["Step"]
        .str.replace("task_", "", regex=False)
        .astype(int)
    )

    # ========================================================
    # Daten für HDR und UI Curve vorbereiten
    # ========================================================

    # Dataframe nach Steps sortieren
    eis_results_df = eis_results_df.sort_values(["Loop 1 number", "Step number"]).reset_index(drop=True)

    # Dict zum Speichern der Kenlinien-Dataframes
    ui_curves = {}

    # Groupby Kennlinie nach den Logik Regeln
    for group_id, group_df in eis_results_df.groupby(["Loop 1 number", "Task"],dropna=False):

        group_df = group_df.sort_values("Step number").reset_index(drop=True)

        loop1, task = group_id

        current_value = None
        curve_number = 1
        list_of_indices = []
        curve_id = ()
        start_index = None
        last_index = None

        if task == "PEIS":
            hold_value = "Hold voltage"
        elif task == "GEIS":
            hold_value = "Hold current"
        else:
            continue

        #Richtung der Kennlinie: absteigend/aufsteigend
        curve_direction = None
        direction_broken = False

        for index, row in group_df.iterrows():

            if current_value is None:
                list_of_indices.append(index)
                current_value = row[hold_value]
                start_index = index
                last_index = index
                continue

            direction_broken = (curve_direction == "ascending" and row[hold_value] <= current_value) or (
                        curve_direction == "descending" and row[hold_value] >= current_value)

            if direction_broken:
                #save last curve
                end_index = last_index
                curve_id = (loop1, task, curve_number,start_index, end_index)
                ui_curves[curve_id] = group_df.iloc[start_index:end_index+1].copy() # hier ggf. 3er Kriterium mit Doku

                # new curve
                curve_number += 1

                # Clean up und Daten der neuen Zeile übernehmen
                list_of_indices = [index]
                current_value = row[hold_value]
                last_index = index
                start_index = index
                curve_id = ()
                curve_direction = None

            else:
                # Descending/Aschending Bedingung in Durchlauf 1 - also 2te Zeile
                if curve_direction is None:
                    if row[hold_value] < current_value:
                        curve_direction = "descending"
                    elif row[hold_value] > current_value:
                        curve_direction = "ascending"
                    # hier kann theoretisch noch ein Abbruch und eine Fehlermeldung stehen
                list_of_indices.append(index)
                current_value = row[hold_value]
                last_index = index


        # save last curve of the loop
        if start_index is not None and last_index is not None:
            end_index = last_index
            curve_id = (loop1, task, curve_number, start_index, end_index)
            ui_curves[curve_id] = group_df.iloc[start_index:end_index + 1].copy()  # hier ggf. 3er Kriterium mit Doku

    # OPTIONAL: für kompliziertere Source-Files:
    # gleiche Source file können wir bei dieser Auswertung als gegeben ansehen - muss ggf. zugefügt werden

    # OPTIONAL: Nicht ausgewertete (keine Kennlinie nach Kriterium als Parameter dokumentieren, ggf. mit Step nr.)
    # ggf. auch ignore reasons angeben


    # ========================================================
    # Daten abrufen für HFR-Auftragung und U/I-Kurve
    # ========================================================

    # Aus dem Dataframes in Dict Konstruktion muss für jede Kennlinie ein Dataframe extrahiert werden
    for curve_id, curve_df in ui_curves.items():
        (loop1, task, curve_number, start_index, end_index) = curve_id

        # start_index und end_index sind nur für Dokumentation relevant
        # loop, task, curve_number werden auch für die Plots gebraucht

        #Startspannung/Startstrom und Endspannung/Endstrom ermitteln
        starting_voltage = curve_df.iloc[0]["Hold voltage"]
        ending_voltage = curve_df.iloc[-1]["Hold voltage"]
        starting_current = curve_df.iloc[0]["Hold current"]
        ending_current = curve_df.iloc[-1]["Hold current"]

        # U/I Datenpunkte aus den Holds - egal ob PEIS oder GEIS
        hold_currents = curve_df["Hold current"]
        hold_voltages = curve_df["Hold voltage"]

    # ========================================================
    # Plot U/I Kennlinie
    # ========================================================

        ui_curve_plot(output_dir, task, loop1, hold_voltages, hold_currents, starting_voltage, ending_voltage,
                      starting_current, ending_current, curve_number, show_plot)


    # ========================================================
    # Plot HFR-Kennlinie
    # ========================================================

        hfr_estimates = curve_df["HFR estimate"]

        hfr_plot(output_dir, task, loop1, hfr_estimates, hold_currents, starting_voltage, ending_voltage,
                      starting_current, ending_current, curve_number, show_plot)


    # ========================================================
    # Dokumentation der EIS-Steps
    # ========================================================

    # die Doku der einzelnen Steps kann aus eis_results_df extrahiert werden

    # Hier sind daher keine weiteren Schritt notwendig

    # ========================================================
    # Dokumentation der Kennlinien
    # ========================================================

    curve_doc_rows = []

    for curve_id, curve_df in ui_curves.items():
        loop1, task, curve_number, start_index, end_index = curve_id

        if task == "PEIS":
            controlled_quantity = "voltage"
            start_control_value = round(curve_df["Hold voltage"].iloc[0],2)
            end_control_value = round(curve_df["Hold voltage"].iloc[-1],2)
        elif task == "GEIS":
            controlled_quantity = "current"
            start_control_value = round(curve_df["Hold current"].iloc[0],2)
            end_control_value = round(curve_df["Hold current"].iloc[-1],2)
        else:
            continue

        if end_control_value > start_control_value:
            curve_direction = "ascending"
        elif end_control_value < start_control_value:
            curve_direction = "descending"
        else:
            curve_direction = "constant"

        ok_points = (curve_df["evaluation_status"] == "ok").sum() #.all falls man nur ja/nein wissen will, im df True =1, False = 0
        non_ok_points = len(curve_df) - ok_points
        curve_status = "ok" if non_ok_points == 0 else "check"

        curve_doc_rows.append({
            "Loop 1 number": loop1,
            "Task": task,
            "Curve number": curve_number,
            "Controlled quantity": controlled_quantity,
            "Curve direction": curve_direction,
            "Curve length": len(curve_df),
            "Start step": curve_df["Step"].iloc[0],
            "End step": curve_df["Step"].iloc[-1],
            "Min voltage": round(curve_df["Hold voltage"].min(), 2),
            "Max voltage": round(curve_df["Hold voltage"].max(), 2),
            "Min current": round(curve_df["Hold current"].min(), 2),
            "Max current": round(curve_df["Hold current"].max(), 2),
            "OK points": ok_points,
            "Non-OK points": non_ok_points,
            "Curve evaluation status": curve_status,
            "Min HFR -Imag": round(curve_df["HFR -Imag"].min(), 4),
            "Max HFR -Imag": round(curve_df["HFR -Imag"].max(), 4),
        })

    curve_doc_df = pd.DataFrame(curve_doc_rows) #dict in Liste wird zu df

    return eis_results_df, curve_doc_df