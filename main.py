import sys
from pathlib import Path
from biologic_bcs915_csv_steps_to_csv import steps_to_csv
from corrected_files_from_raw_csv import corrected_files
from plot_from_corrected_csv import plot_corrected
from dataframe_summary import dataframe_summary
from evaluate_from_corrected_csv import evaluate
from biologic_mpr_steps_to_csv import mpr_to_csv
import csv

def main():

    # ========================================================
    # Anwendung
    # ========================================================

    # BCS 915: *EINE* CSV-Datei mit CV, VS, CC, GEIS, PEIS
    # BCS 815: Beliebig viele MPR-Dateien mit CstV oder LSV

    # EIS und MB aktuell nicht für BCS 815

    # ========================================================
    # Einstellungen Datenquelle
    # ========================================================

    # ==============   BCS 815 oder 915?   ===================
    # 815 verwendet MPR über Galvani (aktuell nur VS und CV)
    # 915 eine große CSV mit allen Techniken (Standard)

    # 815 für alten BCS 815, alles andere ist 915 (Standard)
    potentiostat = "815"

    # ========================================================
    # Einstellungen Plots
    # ========================================================

    # =================   Show Plots?   ======================

    plot_show_plots = False

    # ================   Overlay Plots?   ====================

    overlay_plots = False

    # ==============   Overlay Settings    ===================

    # Welche Messungen kommen in ein Overlay?
    # step: "task_x"
    # task: Taskname nach BCS 915 Nomenklatur -> CV für Constant Voltage, VS für LSV, PEIS/GEIS für Impedanz
    # loop: Nummer des Loops als integer
    # segment: Normalerweise main, für PEIS/GEIS: hold = CV Anteil, eis = EIS Anteil

    overlay_plot_name = "Overlay_Plot"

    overlay_plots_dict = {
        "step": ("task_5", "task_9", "task_11"),
        "task": ("PEIS", "PEIS", "PEIS"),
        "loop": (1, 1, 1),
        "segment": ("eis", "eis", "eis")
    }

    # NOTE: nur Overlays für die gleiche Methode sind implementiert! → "task" müssen alle gleich sein!

    # ========================================================
    # Einstellungen LSV Extended Evaluation
    # ========================================================


    # Ausführen?
    lsv_extended = True # CURRENT LSV NOCH HINZUFÜGEN !!!!!!!!!!!

    # Auswahl der Smoothing Methode -> "rolling für rolling mean, sonst automatisch "bucket"
    smoothing_method = "rolling"
    prominence = 1.1

    # =================   Rolling Mean   ======================
    # Gute Rauschunterdrückung aber schneidet am Anfang einige Punkte als NaN ab!

    if smoothing_method == "rolling":

        # Rauschunterdrückung: Gibt an über wie viele Punkte gemittelt wird
        # Im Zweifel prüfen wie viele Punkte / mV aufgenommen wurden
        # Wichtig
        current_smoothing_1st_derivative = 10 # → Glättet den Strom für 1. Ableitung
        current_smoothing_2nd_derivative = 50 # → Glättet den Strom für 2. Ableitung
        derivative_smoothing_2nd_derivative = 120 # → Glättet die 1. Ableitung vor der 2.

        # Savgol Kriterien
        # Savgol Widnow Points -> wie viele Punkte verwendet der Savgol Filter für Fits
        # Muss < Feature-Breite sein -> Point Distance x savgol_window_size < Feature-Breite
        savgol_window_points = 91

        # Bucket Parameters not used
        bucket_width = None
        min_feature_size = None
        feature_points = None

    # ===============   Bucket Smoothing   ====================
    # Bucket Smoothing NUR bei vielen Datenpunkten oder wenig verrauschten Daten!
    # Vorteil: Schneidet keine Punkte ab

    else:  # Else -> Smoothing Method wird immer "Bucket"
        # Bucket Parameters
        bucket_width = 0.01  # in V
        min_feature_size = 0.1  # in V
        feature_points = round(min_feature_size / bucket_width)
        savgol_window_points = round(min_feature_size / bucket_width / 2)

        # Savgol Kriterien
        if savgol_window_points % 2 == 0:
            savgol_window_points = savgol_window_points + 1
        if savgol_window_points < 7:
            raise ValueError("Not enough savgol window points provided")
        elif 7 <= savgol_window_points < 10:
            print("Savgol window points low, this can be inaccurate")


        #Rolling Parameters not used
        current_smoothing_1st_derivative = None
        current_smoothing_2nd_derivative = None
        derivative_smoothing_2nd_derivative = None


    # ==========   Peak Analysis   ===============

    # Auf welchen Höhen werden Peakbreiten analysiert (-> CSV)
    peak_width_rel_heights = [0.5, 0.8, 0.95]

    # Auf welchen relativen Peakhöhen liegen die Peakmarker in den Plots
    plot_peak_width_rel_height = 0.5

    # ==========   LSV Sensitivity Analysis   ===============

    lsv_sensitivity_plots = False

    lsv_sensitivity_analysis = False

    lsv_sensitivity_overlay_plots = False

    lsv_sensitivity_configs = [
        {
            "label": "low_smoothing",
            "current_smoothing_1st_derivative": 10,
            "current_smoothing_2nd_derivative": 10,
            "derivative_smoothing_2nd_derivative": 50,
            "savgol_window_points": 101,
            "prominence": 1.3,
            "bucket_width": 0.05,
            "min_feature_size": 0.1,
            "smoothing_method": smoothing_method,
            "peak_width_rel_heights": peak_width_rel_heights,
            "plot_peak_width_rel_height": plot_peak_width_rel_height,
        },
        {
            "label": "medium_smoothing",
            "current_smoothing_1st_derivative": 40,
            "current_smoothing_2nd_derivative": 30,
            "derivative_smoothing_2nd_derivative": 100,
            "savgol_window_points": 101,
            "prominence": 1.4,
            "bucket_width": 0.025,
            "min_feature_size": 0.1,
            "smoothing_method": smoothing_method,
            "peak_width_rel_heights": peak_width_rel_heights,
            "plot_peak_width_rel_height": plot_peak_width_rel_height,
        },
        {
            "label": "high_smoothing",
            "current_smoothing_1st_derivative": 70,
            "current_smoothing_2nd_derivative": 75,
            "derivative_smoothing_2nd_derivative": 150,
            "savgol_window_points": 101,
            "prominence": 1.4,
            "bucket_width": 0.05,
            "min_feature_size": 0.1,
            "smoothing_method": smoothing_method,
            "peak_width_rel_heights": peak_width_rel_heights,
            "plot_peak_width_rel_height": plot_peak_width_rel_height,
        },
    ]


    # ========================================================
    # Einstellungen LSV Fits
    # ========================================================

    # Voltage Angaben in V

    lsv_linear_fit = False
    fit_start_voltage = 2.3
    fit_end_voltage = 2.5


    # ========================================================
    # Einstellungen Evaluate
    # ========================================================

    # =============   Kennlinien auswerten?   =================

    # für Kennlinien: "True", für Einzelmessungen "False"
    evaluate_curves = False

    # Sollen Plots gezeigt werden in "evaluate"?
    evaluate_show_plots = False

    # ========================================================
    # Folders
    # ========================================================

    raw_input_dir = Path("input")
    steps_raw_dir = Path("steps_raw")
    steps_corrected_dir = Path("steps_corrected")
    plot_dir = Path("plots")
    evaluate_dir = Path("evaluation")

    # ========================================================
    # Dateien aufrufen
    # ========================================================
    if potentiostat == "815":
        raw_counts, skipped_rows = mpr_to_csv(raw_input_dir, steps_raw_dir)
    else:
        raw_counts, skipped_rows = steps_to_csv(raw_input_dir, steps_raw_dir)
    corrected_counts = corrected_files(steps_raw_dir, steps_corrected_dir)
    plot_results, lsv_lines_cut, eis_hold_values, width_df = plot_corrected(
                                                                            steps_corrected_dir,
                                                                            plot_dir,plot_show_plots,
                                                                            lsv_extended,
                                                                            current_smoothing_1st_derivative,
                                                                            current_smoothing_2nd_derivative,
                                                                            derivative_smoothing_2nd_derivative,
                                                                            bucket_width,
                                                                            savgol_window_points,
                                                                            prominence,
                                                                            smoothing_method,
                                                                            min_feature_size,
                                                                            lsv_sensitivity_plots,
                                                                            lsv_sensitivity_analysis,
                                                                            lsv_sensitivity_configs,
                                                                            lsv_sensitivity_overlay_plots,
                                                                            peak_width_rel_heights,
                                                                            plot_peak_width_rel_height,
                                                                            overlay_plots,
                                                                            overlay_plots_dict,
                                                                            overlay_plot_name,
                                                                            lsv_linear_fit,
                                                                            fit_start_voltage,
                                                                            fit_end_voltage
                                                                            )


    if evaluate_curves:
        eis_results_df, curve_doc_df = evaluate(steps_corrected_dir, evaluate_dir, eis_hold_values, evaluate_show_plots)

    # ========================================================
    # Dokumentationsdatei für Steps und Plot, Print
    # ========================================================

    output_dir = Path(plot_dir)
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / "inline_documentation.csv"

    with  open(output_path, "w", newline="") as output_file:
        writer = csv.writer(output_file, delimiter=",")

        header = ["Step.", "Method", "Loop", "Segment", "Rows written", "Rows skipped", "Rows corrected", "Plot", "Lines cut"]
        writer.writerow(header)

        print()
        print("================================================================================================")
        print("STEP, TASK, LOOP, SEGMENT, LINES_RAW, LINES_SKIPPED, LINES_CORRECTED, PLOT_STATUS, LSV_LINES_CUT")
        print("================================================================================================")
        print()

        for measurement_id in raw_counts:
            step, task, loop1, segment = measurement_id

            raw_rows = raw_counts[measurement_id]
            raw_skipped = skipped_rows.get(measurement_id, "n/a")
            corrected_rows = corrected_counts.get(measurement_id, "")
            plot_status = plot_results.get(measurement_id, "not processed")
            lsv_status = lsv_lines_cut.get(measurement_id, "n/a")

            print(step, task, loop1, segment, raw_rows, raw_skipped, corrected_rows, plot_status, lsv_status)
            writer.writerow([step, task, loop1, segment, raw_rows, raw_skipped, corrected_rows, plot_status, lsv_status])

    # Dataframe Dokumentation
    dataframe_summary(steps_corrected_dir, plot_dir)

    # ========================================================
    # Dokumentationsdatei für Evaluate, Print
    # ========================================================

    if lsv_extended:

        evaluate_dir.mkdir(parents=True, exist_ok=True)

        if not width_df.empty:
            width_df.to_csv(evaluate_dir / "Peak_Evaluation_Data.csv", index=False)

            print()
            print("================================================================================================")
            print("Peak Data Summary")
            print("================================================================================================")
            print()

            print(width_df.to_string(index=False))

    if evaluate_curves:

        evaluate_dir.mkdir(parents=True, exist_ok=True)

        eis_results_df.to_csv(evaluate_dir / "eis_step_evaluation_summary.csv", index=False)
        curve_doc_df.to_csv(evaluate_dir / "eis_curve_evaluation_summary.csv", index=False)

        print()
        print("================================================================================================")
        print("Evaluation Curves Summary")
        print("================================================================================================")
        print()

        evaluation_curves_overview_columns = [
            "Loop 1 number",
            "Task",
            "Curve number",
            "Curve direction",
            "Curve length",
            "Min voltage",
            "Max voltage",
            "Min current",
            "Max current",
            "Curve evaluation status",
        ]

        print(curve_doc_df[evaluation_curves_overview_columns].to_string(index=False))


if __name__ == "__main__":
    main()