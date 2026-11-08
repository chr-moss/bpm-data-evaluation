
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
import settings

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

def peis_nyquist(real_impedance: pd.Series, imaginary_impedance: pd.Series,ac_amplitude: pd.Series, hold_voltage, step, show_plot: bool, loop1, output_dir: Path, file_path, cleaned: bool):
     amplitude_label = f"{ac_amplitude.iloc[0] * 1000:g}mV"
     step_label = step.replace("task_", "")
     voltage_label = voltage_number(hold_voltage)
     plt.figure(figsize=[6.4*1.3,4.8*1.3])
     plt.plot(real_impedance, imaginary_impedance, marker = "o", label = f"{ac_amplitude.iloc[0] * 1000:g}mV at {voltage_label}")
     plt.legend()
     plt.xlabel("Re / Ohm", fontsize = 14, labelpad = 10)
     plt.ylabel("-Im / Ohm", fontsize = 14, labelpad = 8)
     plt.grid(True, alpha=0.3)

     if cleaned:
         folder_name = "Nyquist_Plots_cleaned"
         suffix = f"PEIS_cl_{ac_amplitude.iloc[0] * 1000:g}mV"
     else:
         folder_name = "Nyquist_Plots"
         suffix = f"PEIS_{ac_amplitude.iloc[0] * 1000:g}mV"

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

def geis_nyquist(real_impedance: pd.Series, imaginary_impedance: pd.Series,ac_amplitude: pd.Series, hold_voltage, step,
                 show_plot: bool, loop1, output_dir: Path, file_path, cleaned: bool):
    amplitude_label = f"{ac_amplitude.iloc[0] * 1000:g}mV"
    step_label = step.replace("task_", "")
    current_label = current_number(hold_voltage)
    plt.figure(figsize=[6.4 * 1.3, 4.8 * 1.3])
    plt.plot(real_impedance, imaginary_impedance, marker="o", label=f"{ac_amplitude.iloc[0] * 1000:g}mV at {current_label}")
    plt.legend()
    plt.xlabel("Re / Ohm", fontsize=14, labelpad=10)
    plt.ylabel("-Im / Ohm", fontsize=14, labelpad=8)
    plt.grid(True, alpha=0.3)

    if cleaned:
        folder_name = "Nyquist_Plots_cleaned"
        suffix = f"GEIS_cl_{ac_amplitude.iloc[0] * 1000:g}mV"
    else:
        folder_name = "Nyquist_Plots"
        suffix = f"GEIS_{ac_amplitude.iloc[0] * 1000:g}mV"

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
        plot_dir = output_dir / "EIS_Curves"
        plot_dir.mkdir(parents=True, exist_ok=True)
        plot_path = plot_dir / f"{curve_number}_{task}_HFR.png"
    else:
        plot_dir = output_dir / "EIS_Curves" / f"Loop_{loop1:.0f}"
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
        plot_dir = output_dir / "EIS_Curves"
        plot_dir.mkdir(parents=True, exist_ok=True)
        plot_path = plot_dir / f"{curve_number}_{task}_UI.png"
    else:
        plot_dir = output_dir / "EIS_Curves" / f"Loop_{loop1:.0f}"
        plot_dir.mkdir(parents=True, exist_ok=True)
        plot_path = plot_dir / f"{curve_number}_{task}_{loop1:.0f}_UI.png"
    # plt.tight_layout() -> nicht verwendet, da ohne padding nicht mehr symmetrisch
    plt.savefig(plot_path , dpi = 300)
    if show_plot:
        plt.show()
    plt.close()

def hfr_overlay_plot_ampvar(output_dir, loop1, task, curve_df_list, show_plot):

    plt.figure(figsize=[6.4 * 1.3, 4.8 * 1.3])

    for curve_df in curve_df_list:

        hold_voltages = curve_df["Hold voltage"]
        hfr_estimates = curve_df["HFR estimate"]

        amplitude = curve_df["AC amplitude /V"].iloc[0] * 1000
        plot_label = f"{amplitude:g} mV"

        plt.plot(
            hold_voltages,
            hfr_estimates,
            marker="o",
            label=plot_label
        )

    plt.legend()
    plt.xlabel("U / V", fontsize=14, labelpad=10)
    plt.ylabel("HFR / Ohm", fontsize=14, labelpad=8)
    plt.grid(True, alpha=0.3)

    if pd.isna(loop1):
        plot_dir = output_dir / "EIS_Curves" / "Overlay"
    else:
        plot_dir = output_dir / "EIS_Curves" / "Overlay" / f"Loop_{loop1:.0f}"

    plot_dir.mkdir(parents=True, exist_ok=True)
    plot_path = plot_dir / f"{task}_HFR_overlay_ampvar.png"

    plt.savefig(plot_path, dpi=300)

    if show_plot:
        plt.show()

    plt.close()

def ui_overlay_plot_ampvar(output_dir, loop1, task, curve_df_list, show_plot):

    plt.figure(figsize=[6.4 * 1.3, 4.8 * 1.3])

    for curve_df in curve_df_list:
        hold_voltages = curve_df["Hold voltage"]
        hold_currents = curve_df["Hold current"]

        amplitude = curve_df["AC amplitude /V"].iloc[0] * 1000
        plot_label = f"{amplitude:g} mV"

        plt.plot(
            hold_voltages,
            hold_currents,
            marker="o",
            label=plot_label
        )

    plt.legend()
    plt.xlabel("U / V", fontsize=14, labelpad=10)
    plt.ylabel("I / A", fontsize=14, labelpad=8)
    plt.grid(True, alpha=0.3)

    if pd.isna(loop1):
        plot_dir = output_dir / "EIS_Curves" / "Overlay"
    else:
        plot_dir = output_dir / "EIS_Curves" / "Overlay" / f"Loop_{loop1:.0f}"

    plot_dir.mkdir(parents=True, exist_ok=True)
    plot_path = plot_dir / f"{task}_UI_overlay_ampvar.png"

    plt.savefig(plot_path, dpi=300)

    if show_plot:
        plt.show()

    plt.close()


def peis_nyquist_overlay(output_dir, curve_spectra_dict, eis_results_dict, show_plot):

    # AKTUELL NUR CURVES UND NICHT AMPVAR AUF EINER SPANNUNG

    for cleaned_counter in (False, True):

        for curve_id, eis_data_dict in curve_spectra_dict.items():

            loop1, task, curve_number, start_index, end_index = curve_id

            if task != "PEIS" or not eis_data_dict:
                continue

            cleaning_failed = False

            first_eis_df = next(iter(eis_data_dict.values()))
            amplitude = first_eis_df["AC amplitude /V"].iloc[0] * 1000
            amplitude_label = f"{amplitude:g}mV"

            plt.figure(figsize=[6.4 * 1.3, 4.8 * 1.3])

            for measurement_id, eis_df in eis_data_dict.items():

                # Measurement ID
                step, task, loop_id, segment = measurement_id

                # Cleaned df erzeugen
                if cleaned_counter:
                    hfr_index = eis_results_dict[measurement_id]["HFR index"]
                    if hfr_index is None:
                        cleaning_failed = True
                        continue
                    eis_cleaned_df = eis_df.iloc[hfr_index:]
                    plot_df = eis_cleaned_df
                else:
                    plot_df = eis_df

                voltage = plot_df["U /V"]
                current = plot_df["I /A"]
                frequency = plot_df["Frequency /Hz"]
                impedance_module = plot_df["Impedance module /Ohms"]
                impedance_phase = plot_df["Impedance phase /rad"]
                real_impedance = plot_df["Real impedance /Ohms"]
                imaginary_impedance = plot_df["- Imaginary impedance /Ohms"]
                hold_voltage = eis_results_dict[measurement_id]["Hold voltage"]
                ac_amplitude = eis_results_dict[measurement_id]["AC amplitude /V"] * 1000


                #Labels vorbereiten
                step_label = step.replace("task_", "")
                voltage_label = voltage_number(hold_voltage)

                label_variant = "amplitude"  # step oder amplitude, voltage wird immer angezeigt

                if label_variant == "amplitude":
                    plot_label = f"{ac_amplitude:g} mV @ {voltage_label}"
                else:
                    plot_label = f"Step {step_label} at {voltage_label}"

                # Einen Nyquist Plot erstellen
                plt.plot(
                    real_impedance,
                    imaginary_impedance,
                    marker="o",
                    label=plot_label
                )

            if cleaning_failed:
                plt.close()
                continue
            # Plot auffüllen / Achsen erstellen
            plt.legend()
            plt.xlabel("Re / Ohm", fontsize=14, labelpad=10)
            plt.ylabel("-Im / Ohm", fontsize=14, labelpad=8)
            plt.grid(True, alpha=0.3)

            # fertigen Plot speichern
            folder_name = "Nyquist_Plots_cleaned" if cleaned_counter else "Nyquist_Plots"

            if pd.isna(loop1) or loop1 == "":
                plot_dir = output_dir / folder_name / "Overlay"
                plot_dir.mkdir(parents=True, exist_ok=True)
                plot_path = plot_dir / f"{task}_Curve_{curve_number:02d}_{amplitude_label}_overlay.png"
            else:
                plot_dir = output_dir / folder_name / f"Overlay_Loop_{loop1:.0f}"
                plot_dir.mkdir(parents=True, exist_ok=True)
                plot_path = plot_dir / f"{task}_Loop_{loop1:.0f}_Curve_{curve_number:02d}_{amplitude_label}_overlay.png"

            # plt.tight_layout() -> nicht verwendet, da ohne padding nicht mehr symmetrisch

            plt.savefig(plot_path, dpi=300)
            if show_plot:
                plt.show()
            plt.close()


def amplitude_nyquist_overlay(output_dir, hold_spectra_dict, eis_results_dict, show_plot):

    # Nyquist-Overlay mehrerer AC-Amplituden bei gleicher HOLD-Spannung

    for cleaned_counter in (False, True):

        for hold_group_id, eis_data_dict in hold_spectra_dict.items():

            loop_id, task, block_number = hold_group_id

            if task != "PEIS" or not eis_data_dict:
                continue

            # HOLD-Spannung für den Dateinamen ermitteln
            first_measurement_id = next(iter(eis_data_dict))
            hold_voltage = eis_results_dict[first_measurement_id]["Hold voltage"]
            hold_voltage_label = voltage_number(hold_voltage)

            cleaning_failed = False
            plt.figure(figsize=[6.4 * 1.3, 4.8 * 1.3])

            for measurement_id, eis_df in eis_data_dict.items():

                # Measurement ID
                step, task, loop_id, segment = measurement_id

                # Cleaned df erzeugen
                if cleaned_counter:
                    hfr_index = eis_results_dict[measurement_id]["HFR index"]
                    if hfr_index is None:
                        cleaning_failed = True
                        continue
                    eis_cleaned_df = eis_df.iloc[hfr_index:]
                    plot_df = eis_cleaned_df
                else:
                    plot_df = eis_df

                voltage = plot_df["U /V"]
                current = plot_df["I /A"]
                frequency = plot_df["Frequency /Hz"]
                impedance_module = plot_df["Impedance module /Ohms"]
                impedance_phase = plot_df["Impedance phase /rad"]
                real_impedance = plot_df["Real impedance /Ohms"]
                imaginary_impedance = plot_df["- Imaginary impedance /Ohms"]
                hold_voltage = eis_results_dict[measurement_id]["Hold voltage"]
                ac_amplitude = eis_results_dict[measurement_id]["AC amplitude /V"] * 1000


                #Labels vorbereiten
                step_label = step.replace("task_", "")
                voltage_label = voltage_number(hold_voltage)
                amplitude_label = f"{ac_amplitude:g}mV"

                label_variant = "amplitude"  # step oder amplitude, voltage wird immer angezeigt

                if label_variant == "amplitude":
                    plot_label = f"{ac_amplitude:g} mV @ {voltage_label}"
                else:
                    plot_label = f"Step {step_label} at {voltage_label}"

                # Einen Nyquist Plot erstellen
                plt.plot(
                    real_impedance,
                    imaginary_impedance,
                    marker="o",
                    label=plot_label
                )

            if cleaning_failed:
                plt.close()
                continue
            # Plot auffüllen / Achsen erstellen
            plt.legend()
            plt.xlabel("Re / Ohm", fontsize=14, labelpad=10)
            plt.ylabel("-Im / Ohm", fontsize=14, labelpad=8)
            plt.grid(True, alpha=0.3)

            # fertigen Plot speichern
            folder_name = "Nyquist_Plots_cleaned" if cleaned_counter else "Nyquist_Plots"

            if pd.isna(loop_id) or loop_id == "":
                plot_dir = output_dir / folder_name / "Amplitude_Variation"
                plot_dir.mkdir(parents=True, exist_ok=True)
                plot_path = plot_dir / f"{task}_Block_{block_number:02d}_{hold_voltage_label}_overlay.png"
            else:
                plot_dir = output_dir / folder_name / f"Amplitude_Variation_Loop_{loop_id:.0f}"
                plot_dir.mkdir(parents=True, exist_ok=True)
                plot_path = plot_dir / f"{task}_Loop_{loop_id:.0f}_Block_{block_number:02d}_{hold_voltage_label}_overlay.png"

            # plt.tight_layout() -> nicht verwendet, da ohne padding nicht mehr symmetrisch
            plt.savefig(plot_path, dpi=300)
            if show_plot:
                plt.show()
            plt.close()


# ========================================================
# Hauptfunktion Start
# ========================================================

def evaluate(input_folder: Path, output_folder: Path, eis_hold_values, show_plot):

    """
    # ========================================================
    # Datenstrukturen und zentrale Variablen
    # ========================================================

    # Einzelmessungen
    # df                    DataFrame: vollständig eingelesene Messdatei
    # eis_df                DataFrame: gültige EIS-Datenpunkte einer Messung
    # eis_hf                DataFrame: Hochfrequenzbereich des EIS-Spektrums
    # eis_cleaned_df        DataFrame: EIS-Spektrum ab dem erkannten HFR-Punkt

    # Identifikatoren
    # measurement_id        tuple: (step, task, loop_id, segment)
    # hold_id               tuple: (step, task, loop_id, "hold")
    # curve_id              tuple: (loop1, task, curve_number, start_index, end_index)
    # curve_counter_id      tuple: (loop_id, task), Schlüssel für die Kurvennummerierung

    # EIS-Auswertung
    # eis_hold_values       dict: hold_id -> (Hold-Spannung, Hold-Strom)
    # eis_results_dict      dict: measurement_id -> dict mit Auswertungsergebnissen
    # eis_spectra_dict      dict: measurement_id -> vollständiger eis_df
    # result_rows           list[dict]: Ergebniszeilen für den DataFrame
    # result_row_dict       dict: eine Ergebniszeile mit ID und Auswertungswerten
    # eis_results_df        DataFrame: eine Zeile pro ausgewerteter EIS-Messung

    # Gruppierung und Kennlinienerkennung
    # group_df              DataFrame: Messungen gleicher Loop und Task
    # hold_block            DataFrame: zusammenhängende EIS-Steps gleicher HOLD-Spannung
    # hold_voltage_rounded  Series: gerundete HOLD-Spannungen zur Blockerkennung
    # block_id              Series: Nummer des zusammenhängenden Spannungsblocks
    # step_amplitudes       Series: AC-Amplituden der EIS-Steps eines Blocks
    # group_id_amplitudes   tuple: (loop1, task, ac_amplitude)
    # group_df_amplitudes   DataFrame: Messungen dieser Amplitudengruppe
    # measurement_row       Series: einzelne Zeile aus group_df_amplitudes
    # curve_numbers         dict: curve_counter_id -> zuletzt verwendete Kurvennummer
    # eis_curves_dict       dict: curve_id -> DataFrame einer erkannten Kennlinie
    # curve_df              DataFrame: ausgewertete EIS-Messungen einer Kennlinie

    # Kennlinien-Overlays (U/I und HFR)
    # group_id_curve_overlay tuple: (loop_id, task)
    # overlay_groups        dict: group_id_curve_overlay -> Liste von curve_df
    # curve_df_list         list[DataFrame]: Kennlinien einer Overlay-Gruppe
    # curve_overlay_amplitudes set: unterschiedliche AC-Amplituden dieser Gruppe

    # Dokumentation
    # curve_doc_rows        list[dict]: Dokumentationszeilen der Kennlinien
    # curve_doc_df          DataFrame: eine Zeile pro erkannter Kennlinie
    """

    # ========================================================
    # Container für Dokumentation
    # ========================================================

    # Container für Dokumentation
    eis_results_dict = {}

    # Container für vollständige EIS-Spektren
    eis_spectra_dict = {}

    # Container für Hold Spectra Dict - Amplitudenvariation
    hold_spectra_dict = {}

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
        task = df["Task"].iloc[0]
        loop1 = df["Loop 1 number"].iloc[0]
        loop_id = None if pd.isna(loop1) else loop1
        segment = df["Segment"].iloc[0]

        measurement_id = (df["Step"].iloc[0], task, loop_id, segment)

        if task not in ["PEIS", "GEIS"] or segment != "eis":
            continue

        # ========================================================
        # df und Series erzeugen -> eis_df und eis_spectra_dict
        # ========================================================

        eis_df = df[
            df["Frequency /Hz"].notna()
            & df["Real impedance /Ohms"].notna()
            & df["- Imaginary impedance /Ohms"].notna()
            ].sort_values("Frequency /Hz", ascending=False).reset_index(drop=True)

        if eis_df.empty:
            eis_results_dict[measurement_id] = {
                "Hold voltage": "n/a",
                "Hold current": "n/a",
                "EIS points": "n/a",
                "HFR estimate": "n/a",
                "HFR frequency": "n/a",
                "HFR -Imag": "n/a",
                "HF points used": "n/a",
                "HF cleaning points removed": "n/a",
                "AC amplitude /V": "n/a",
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
        ac_amplitude = eis_df["AC amplitude /V"]

        hold_id = (step, task, loop_id, "hold")

        # EIS Spectra dict für Overlay Plots erzeugen
        eis_spectra_dict[measurement_id] = eis_df.copy()

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
            eis_results_dict[measurement_id] = {
                "Hold voltage": "n/a",
                "Hold current": "n/a",
                "EIS points": "n/a",
                "HFR estimate": "n/a",
                "HFR frequency": "n/a",
                "HFR -Imag": "n/a",
                "HF points used": "n/a",
                "HF cleaning points removed": "n/a",
                "AC amplitude /V": "n/a",
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
            geis_nyquist(real_impedance, imaginary_impedance,ac_amplitude, hold_current, step, show_plot, loop1, output_dir, file_path, cleaned)
        elif task == "PEIS":
            peis_nyquist(real_impedance, imaginary_impedance,ac_amplitude, hold_voltage, step, show_plot, loop1, output_dir, file_path, cleaned)


        # Clean - Points über HFR estimate entfernen
        eis_cleaned_df = eis_df.iloc[hfr_index:]
        hf_points_cleaned = len(eis_df) - len(eis_cleaned_df)

        real_impedance_cleaned = eis_cleaned_df["Real impedance /Ohms"]
        imaginary_impedance_cleaned = eis_cleaned_df["- Imaginary impedance /Ohms"]

        # Mit cleaned Datensatz wieder Nyquist Plot funktion aufrufen, entweder mit cleaned True/Fals oder eigene Funktion
        cleaned = True
        if task == "GEIS":
            geis_nyquist(real_impedance_cleaned, imaginary_impedance_cleaned,ac_amplitude, hold_current, step, show_plot, loop1,
                         output_dir, file_path, cleaned)
        elif task == "PEIS":
            peis_nyquist(real_impedance_cleaned, imaginary_impedance_cleaned,ac_amplitude, hold_voltage, step, show_plot, loop1,
                         output_dir, file_path, cleaned)


        # ========================================================
        # EIS Daten speichern
        # ========================================================

        eis_results_dict[measurement_id] = {
            "Hold voltage": hold_voltage,
            "Hold current": hold_current,
            "EIS points": len(eis_df), # Zahl aller EIS Punkte
            "HFR estimate": hfr_estimate, # Re(Z) vom HFR Punkt
            "HFR frequency": hfr_frequency, # f vom HFR Punkt
            "HFR -Imag": hfr_minus_imag, # - Im vom HFR Punkt
            "HF points used": len(eis_hf), # Wie viele Punkte der HF-Teil sind
            "HF cleaning points removed": hf_points_cleaned,
            "AC amplitude /V": ac_amplitude.iloc[0],
            "evaluation_status": "ok",
            "HFR index": hfr_index
        }


    # ========================================================
    # Eis-Results-Dict in Dataframe umwandeln
    # ========================================================

    result_rows = []

    for measurement_id, values in eis_results_dict.items():
        step, task, loop_id, segment = measurement_id #die einzelnen Werte aus dem key holen

        result_row_dict = {
            "Step": step,
            "Task": task,
            "Loop 1 number": loop_id,
            "Segment": segment,
        }

        result_row_dict.update(values) # übernimmt die values als neue Values in row (ein bisschen wie append aber größer)

        result_rows.append(result_row_dict) # Es entsteht eine Liste von dicts -> die kann pandas direkt übernehmen

    ##########################################################################################
    ### HIER KANN EIN FEHLER ENTSTEHEN WENN KEINE EIS MESSUNGEN DRIN SIND: UPDATE SINNVOLL ###
    ##########################################################################################

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

    # Dict zum Speichern der Kennlinien-Dataframes
    eis_curves_dict = {}
    curve_numbers = {}

    # TODO: Fehlgeschlagene EIS-Auswertungen bei der Kennlinienbildung behandeln.
    # "n/a" in Hold-Werten kann bei numerischen Vergleichen Fehler auslösen.
    # Gültige U/I-Betriebspunkte möglichst auch ohne HFR erhalten.

    # Nach Loop und Task gruppieren
    for (loop1, task), group_df in eis_results_df.groupby(
            ["Loop 1 number", "Task"], dropna=False
    ):
        if task != "PEIS":
            continue

        group_df = group_df.sort_values("Step number")

        # Zusammenhängende HOLD-Spannungsblöcke identifizieren
        hold_voltage_rounded = pd.to_numeric(group_df["Hold voltage"], errors="coerce").round(2)
        block_id = hold_voltage_rounded.ne(hold_voltage_rounded.shift()).cumsum()

        # Hold Block sind die Messblöcke bei einer Spannung, enthält alle Spalten aus Group.df
        for block_number, hold_block in group_df.groupby(block_id):

            step_amplitudes = hold_block["AC amplitude /V"].dropna()

            if step_amplitudes.nunique() > 1 and step_amplitudes.duplicated().any():
                raise ValueError(
                    "Repeated AC amplitude within a HOLD block"
                )

            if step_amplitudes.nunique() <= 1:
                continue

            loop_id = None if pd.isna(loop1) else loop1
            hold_group_id = (loop_id, task, block_number)

            hold_spectra_dict[hold_group_id] = {}

            # Rekonstruktion measurement_id aus hold_block
            for _, measurement_row in hold_block.iterrows():
                step = measurement_row["Step"]
                task = measurement_row["Task"]
                loop1 = measurement_row["Loop 1 number"]
                segment = measurement_row["Segment"]

                loop_id = None if pd.isna(loop1) else loop1
                measurement_id = (step, task, loop_id, segment)

                # Zuordnung hold_block zu eis Spektren
                hold_spectra_dict[hold_group_id][measurement_id] = eis_spectra_dict[measurement_id]

    amplitude_nyquist_overlay(output_dir, hold_spectra_dict, eis_results_dict, show_plot)

    # ========================================================
    # Kurven ermitteln
    # ========================================================

    for group_id_amplitudes, group_df_amplitudes in eis_results_df.groupby(["Loop 1 number", "Task", "AC amplitude /V"],dropna=False):

        group_df_amplitudes = group_df_amplitudes.sort_values("Step number").reset_index(drop=True)

        loop1, task, ac_amplitude = group_id_amplitudes

        current_value = None
        loop_id = None if pd.isna(loop1) else loop1
        curve_counter_id = (loop_id, task)
        curve_number = curve_numbers.get(curve_counter_id, 0) + 1
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

        for index, measurement_row in group_df_amplitudes.iterrows():

            if current_value is None:
                current_value = measurement_row[hold_value]
                start_index = index
                last_index = index
                continue

            direction_broken = (curve_direction == "ascending" and measurement_row[hold_value] <= current_value) or (
                        curve_direction == "descending" and measurement_row[hold_value] >= current_value)

            if direction_broken:
                #save last curve
                end_index = last_index
                curve_id = (loop1, task, curve_number,start_index, end_index)
                eis_curves_dict[curve_id] = group_df_amplitudes.iloc[start_index:end_index+1].copy() # hier ggf. 3er Kriterium mit Doku

                # new curve
                curve_number += 1

                # Clean up und Daten der neuen Zeile übernehmen
                current_value = measurement_row[hold_value]
                last_index = index
                start_index = index
                curve_id = ()
                curve_direction = None

            else:
                # Descending/Aschending Bedingung in Durchlauf 1 - also 2te Zeile
                if curve_direction is None:
                    if measurement_row[hold_value] < current_value:
                        curve_direction = "descending"
                    elif measurement_row[hold_value] > current_value:
                        curve_direction = "ascending"
                    # hier kann theoretisch noch ein Abbruch und eine Fehlermeldung stehen
                current_value = measurement_row[hold_value]
                last_index = index


        # save last curve of the loop
        if start_index is not None and last_index is not None:
            end_index = last_index
            curve_id = (loop1, task, curve_number, start_index, end_index)
            eis_curves_dict[curve_id] = group_df_amplitudes.iloc[start_index:end_index + 1].copy()  # hier ggf. 3er Kriterium mit Doku

        curve_numbers[curve_counter_id] = curve_number

    # OPTIONAL: für kompliziertere Source-Files:
    # gleiche Source file können wir bei dieser Auswertung als gegeben ansehen - muss ggf. zugefügt werden

    # OPTIONAL: Nicht ausgewertete (keine Kennlinie nach Kriterium als Parameter dokumentieren, ggf. mit Step nr.)
    # ggf. auch ignore reasons angeben


    # ========================================================
    # Daten abrufen für HFR-Auftragung und U/I-Kurve
    # ========================================================

    # Aus dem Dataframes in Dict Konstruktion muss für jede Kennlinie ein Dataframe extrahiert werden
    for curve_id, curve_df in eis_curves_dict.items():
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
    # Dict erstellen für Gruppierung von Curve Daten
    # ========================================================

    overlay_groups = {}

    for curve_id, curve_df in eis_curves_dict.items():
        loop1, task, curve_number, start_index, end_index = curve_id

        amplitude = curve_df["AC amplitude /V"].iloc[0]

        if pd.isna(amplitude):
            continue

        group_id_curve_overlay = (None if pd.isna(loop1) else loop1, task)

        if group_id_curve_overlay not in overlay_groups:
            overlay_groups[group_id_curve_overlay] = []

        overlay_groups[group_id_curve_overlay].append(curve_df)

    for (loop1, task), curve_df_list in overlay_groups.items():

        curve_overlay_amplitudes = {
            curve_df["AC amplitude /V"].iloc[0]
            for curve_df in curve_df_list  # Ein Set
        }

        if len(curve_overlay_amplitudes) > 1:
            hfr_overlay_plot_ampvar(
                output_dir, loop1, task, curve_df_list, show_plot
            )
            ui_overlay_plot_ampvar(
                output_dir, loop1, task, curve_df_list, show_plot
            )


    # ========================================================
    # Curve Spectra Dict für Nyquist Overlays erzeugen
    # ========================================================

    curve_spectra_dict = {} #äußeres dictionary anlegen

    for curve_id, curve_df in eis_curves_dict.items():

        curve_spectra_dict[curve_id] = {}  # Inneres Dictionary anlegen

        for index, measurement_row in curve_df.iterrows():
            step = measurement_row["Step"]
            task = measurement_row["Task"]
            loop1 = measurement_row["Loop 1 number"]
            segment = measurement_row["Segment"]

            loop_id = None if pd.isna(loop1) else loop1
            measurement_id = (step, task, loop_id, segment)

            eis_df = eis_spectra_dict[measurement_id]

            curve_spectra_dict[curve_id][measurement_id] = eis_df

    peis_nyquist_overlay(output_dir, curve_spectra_dict, eis_results_dict, show_plot)


    # ========================================================
    # Dokumentation der EIS-Steps
    # ========================================================

    # die Doku der einzelnen Steps kann aus eis_results_df extrahiert werden

    # Hier sind daher keine weiteren Schritt notwendig

    # ========================================================
    # Dokumentation der Kennlinien
    # ========================================================

    curve_doc_rows = []

    for curve_id, curve_df in eis_curves_dict.items():
        loop1, task, curve_number, start_index, end_index = curve_id

        if task == "PEIS":
            controlled_quantity = "voltage"
            start_control_value = round(curve_df["Hold voltage"].iloc[0],3)
            end_control_value = round(curve_df["Hold voltage"].iloc[-1],3)
        elif task == "GEIS":
            controlled_quantity = "current"
            start_control_value = round(curve_df["Hold current"].iloc[0],3)
            end_control_value = round(curve_df["Hold current"].iloc[-1],3)
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
            "AC amplitude /V": curve_df["AC amplitude /V"].iloc[0],
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