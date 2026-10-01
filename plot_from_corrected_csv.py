
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
import math
import numpy as np
from scipy.signal import savgol_filter
from scipy.signal import find_peaks, peak_widths

# ========================================================
# Hilfsfunktion LSV Differentials
# ========================================================

def lsv_differentials(smoothing_method,
                      current_smoothing_1st_derivative,
                      current_smoothing_2nd_derivative,
                      derivative_smoothing_2nd_derivative,
                      savgol_window_points,
                      df,
                      bucket_width,
                      min_feature_size,
                      prominence,
                      peak_width_rel_heights,
                      plot_peak_width_rel_height,
                      ):


    peak_width_markers = []
    function_peak_data = []
    step = df["Step"].iloc[0]
    task = df["Task"].iloc[0]
    loop1 = df["Loop 1 number"].iloc[0]

    # ========================================================
    # Rolling mean smoothing
    # ========================================================

    if smoothing_method == "rolling":

        # Current Smooth für den 1. Ableitung plot
        current_smooth_1st = df["I /A"].rolling(window=current_smoothing_1st_derivative,
                                                center=True).mean()  # Note: Hier bleiben zu Beginn ein paar NaN stehen
        d_current = current_smooth_1st.diff()  # Glättung - Mittelwert aus n = window Werten

        # Current Smooth für den 2. Ableitung plot
        current_smooth_2nd = df["I /A"].rolling(window=current_smoothing_2nd_derivative,
                                                center=True).mean()  # Note: Hier bleiben zu Beginn ein paar NaN stehen
        d_current_2nd = current_smooth_2nd.diff()  # Glättung - Mittelwert aus n = window Werten

        # 1. Diff der Spannung - Berechnung der 1. Ableitung für 1. Ableitung Plot
        d_voltage = df["U /V"].diff()
        lsv_derivative_1st = d_current / d_voltage

        # 1. Diff mit eigenem smooth als Basis - Berechnung der 1. Ableitung für 2nd plot
        lsv_derivative_1st_for_2nd = d_current_2nd / d_voltage

        # Smoothing der 1. Ableitung für 2nd plot
        derivative_smoothed_for_2nd = lsv_derivative_1st_for_2nd.rolling(window=derivative_smoothing_2nd_derivative,
                                                                         center=True).mean()

        # Berechnung der zweiten Ableitung nach U aus der smoothed 1. Ableitung
        second_lsv_derivative = derivative_smoothed_for_2nd.diff() / d_voltage

        valid_2nd = second_lsv_derivative.notna()  # Boolean Mask

        voltage_valid = df["U /V"][valid_2nd]
        diff_2nd_valid = second_lsv_derivative[valid_2nd]

        # Savgol Filter und Peakauswertung

        diff_2nd_savgol = savgol_filter(
            diff_2nd_valid.to_numpy(dtype=float),
            window_length=savgol_window_points,
            polyorder=3
        )

        peaks, properties = find_peaks(
            diff_2nd_savgol,
            prominence=prominence,
            distance=100
        )

        peaks_list = peaks.tolist()

        # Spannungsachse für Interpolation
        x_array = voltage_valid.to_numpy(dtype=float)
        x_index = np.arange(len(x_array))

        # Spannungsachse für Interpolation
        x_array = voltage_valid.to_numpy(dtype=float)
        x_index = np.arange(len(x_array))

        # Peakbreiten für mehrere Höhen berechnen
        for current_rel_height in peak_width_rel_heights:
            width_results = peak_widths(
                diff_2nd_savgol,
                peaks_list,
                rel_height=current_rel_height
            )

            widths = width_results[0]
            width_heights = width_results[1]
            left_ips = width_results[2]
            right_ips = width_results[3]

            left_voltages = np.interp(left_ips, x_index, x_array)
            right_voltages = np.interp(right_ips, x_index, x_array)
            peak_width_voltages = right_voltages - left_voltages

            if current_rel_height == plot_peak_width_rel_height:
                peak_width_markers.append({
                    "peak_width_rel_heights": peak_width_rel_heights,
                    "left_voltages": left_voltages,
                    "right_voltages": right_voltages,
                    "width_heights": width_heights
                })

            for i, peak in enumerate(peaks_list):
                function_peak_data.append({
                    "Step": step,
                    "Task": task,
                    "Loop 1 number": loop1,
                    "peak_width_rel_heights": peak_width_rel_heights,
                    "Peak number": i + 1,
                    "Peak voltage / V": voltage_valid.iloc[peak],
                    "Peak height": diff_2nd_savgol[peak],
                    "Prominence": properties["prominences"][i],
                    "Width / mV": peak_width_voltages[i] * 1000,
                    "Left voltage / V": left_voltages[i],
                    "Right voltage / V": right_voltages[i],
                })


    # ========================================================
    # Bucket Smoothing
    # ========================================================

    else:  # else uses the bucket method - also smoothing method = bucket

        lsv_bucket_df = df[["U /V", "I /A"]].dropna().copy()

        # Gruppierungsspalte für Buckets erzeugen
        lsv_bucket_df["Voltage bucket"] = (
                (lsv_bucket_df["U /V"] / bucket_width)
                .round()
                * bucket_width
        )

        # Bucket-Einträge zählen
        bucket_counts = lsv_bucket_df.groupby("Voltage bucket").size()

        # Über Buckets mitteln - Bucket df erzeugen
        bucketed_df = (
            lsv_bucket_df
            .groupby("Voltage bucket", as_index=False)
            .agg({
                "U /V": "mean",
                "I /A": "mean"
            })
            .sort_values("U /V")
            .reset_index(drop=True)
        )

        # 1. Ableitung von Voltage und Current des Bucket df bilden - dI/dU berechnen
        # Hier variieren wir die Buckets erstmal nicht - daher nur eine 1. Ableitung

        voltage_buckets = bucketed_df["Voltage bucket"]
        lsv_bucket_current_diff_1st = bucketed_df["I /A"].diff()
        lsv_bucket_voltage_diff_1st = bucketed_df["U /V"].diff()
        lsv_bucket_derivative_1st = lsv_bucket_current_diff_1st / lsv_bucket_voltage_diff_1st

        # 2. Ableitung von Voltage und Current des Bucket df bilden - d2I/dU2 berechnen

        lsv_bucket_current_diff_of_1st_derivative = lsv_bucket_derivative_1st.diff()
        lsv_bucket_derivative_2nd = lsv_bucket_current_diff_of_1st_derivative / lsv_bucket_voltage_diff_1st

        # Für Savgol Filter NaNs entfernen und Check ob die Daten passen

        valid_bucket_2nd = lsv_bucket_derivative_2nd.notna()

        bucket_voltage_valid = bucketed_df["U /V"][valid_bucket_2nd]
        bucket_diff_2nd_valid = lsv_bucket_derivative_2nd[valid_bucket_2nd]

        if savgol_window_points <= 3:
            raise ValueError("Savgol window must be larger than polyorder=3.")

        if savgol_window_points >= len(bucket_diff_2nd_valid):
            raise ValueError(
                f"Savgol window too large for available data. "
                f"savgol_window_points={savgol_window_points}, "
                f"data_points={len(bucket_diff_2nd_valid)}."
            )

        # Savgol Filter und Peakauswertung

        diff_2nd_savgol = savgol_filter(
            bucket_diff_2nd_valid.to_numpy(dtype=float),
            window_length=savgol_window_points,
            polyorder=3
        )

        peaks, properties = find_peaks(
            diff_2nd_savgol,
            prominence=prominence,
            distance=round(min_feature_size / bucket_width)
        )

        peaks_list = peaks.tolist()

        # Spannungsachse für Interpolation
        x_array = bucket_voltage_valid.to_numpy(dtype=float)
        x_index = np.arange(len(x_array))

        # Peakbreiten für mehrere Höhen berechnen
        for current_rel_height in peak_width_rel_heights:
            width_results = peak_widths(
                diff_2nd_savgol,
                peaks_list,
                rel_height=current_rel_height
            )

            widths = width_results[0]
            width_heights = width_results[1]
            left_ips = width_results[2]
            right_ips = width_results[3]

            left_voltages = np.interp(left_ips, x_index, x_array)
            right_voltages = np.interp(right_ips, x_index, x_array)
            peak_width_voltages = right_voltages - left_voltages

            if current_rel_height == plot_peak_width_rel_height:
                peak_width_markers.append({
                    "peak_width_rel_heights": peak_width_rel_heights,
                    "left_voltages": left_voltages,
                    "right_voltages": right_voltages,
                    "width_heights": width_heights
                })

            for i, peak in enumerate(peaks_list):
                function_peak_data.append({
                    "Step": step,
                    "Task": task,
                    "Loop 1 number": loop1,
                    "peak_width_rel_heights": peak_width_rel_heights,
                    "Peak number": i + 1,
                    "Peak voltage / V": bucket_voltage_valid.iloc[peak],
                    "Peak height": diff_2nd_savgol[peak],
                    "Prominence": properties["prominences"][i],
                    "Width / mV": peak_width_voltages[i] * 1000,
                    "Left voltage / V": left_voltages[i],
                    "Right voltage / V": right_voltages[i],
                })

    if smoothing_method == "rolling":


        # 1. Output: Peakdaten für Doku, 2. Output: Datensätze für Plots -> das hier ist lsv_plot_data
        return function_peak_data, {
            "lsv_derivative_1st": lsv_derivative_1st,
            "voltage_valid": voltage_valid,
            "diff_2nd_valid": diff_2nd_valid,
            "diff_2nd_savgol": diff_2nd_savgol,
            "peaks_list": peaks_list,
            "peak_width_markers": peak_width_markers,
            "voltage": df["U /V"],
        }


    else:

        return function_peak_data, {
            "voltage_buckets": voltage_buckets,
            "lsv_bucket_derivative_1st": lsv_bucket_derivative_1st,
            "bucket_voltage_valid": bucket_voltage_valid,
            "bucket_diff_2nd_valid": bucket_diff_2nd_valid,
            "diff_2nd_savgol": diff_2nd_savgol,
            "peaks_list": peaks_list,
            "peak_width_markers": peak_width_markers,
        }


# ========================================================
# Hilfsfunktionen Sensitivity Plot Overlays
# ========================================================

# Note: Falls der Plot komisch aussieht kann das am Rolling Mean liegen dann kann man mit .notna noch versuchen die NA zu entfernen

def plot_lsv_sensitivity_overlay_1st(
    sensitivity_runs,
    file_path,
    output_dir,
    step,
    loop1,
    show_plots,
):
    plt.figure(figsize=(8, 5))

    for run in sensitivity_runs:
        label = run["label"]
        plot_data = run["plot_data"]
        config = run["config"]

        if config["smoothing_method"] == "rolling":
            x = np.asarray(plot_data["voltage"], dtype=float)
            y = np.asarray(plot_data["lsv_derivative_1st"], dtype=float)

        else:
            x = np.asarray(plot_data["voltage_buckets"], dtype=float)
            y = np.asarray(plot_data["lsv_bucket_derivative_1st"], dtype=float)

        plt.plot(x, y, label=label)

    plt.xlabel("Time /s")
    plt.ylabel("I /A")
    plt.title(f"LSV sensitivity overlay - 1st derivative - Step {step}, Loop {loop1}")
    plt.legend()
    #plt.tight_layout()

    output_path = output_dir / (
        f"{file_path.stem}_step_{step}_loop_{loop1}_sensitivity_overlay_d1LSV.png"
    )

    plt.savefig(output_path, dpi=300)

    if show_plots:
        plt.show()

    plt.close()


def plot_lsv_sensitivity_overlay_2nd(
    sensitivity_runs,
    file_path,
    output_dir,
    step,
    loop1,
    show_plots,
):
    plt.figure(figsize=[8 * 1.1, 5 * 1.1])

    for run in sensitivity_runs:
        label = run["label"]
        plot_data = run["plot_data"]
        config = run["config"]

        if config["smoothing_method"] == "rolling":
            x = np.asarray(plot_data["voltage_valid"], dtype=float)
            y_smooth = np.asarray(plot_data["diff_2nd_savgol"], dtype=float)

        else:
            x = np.asarray(plot_data["bucket_voltage_valid"], dtype=float)
            y_smooth = np.asarray(plot_data["diff_2nd_savgol"], dtype=float)

        peaks_list = plot_data["peaks_list"]

        plt.plot(x, y_smooth, label=label)

        if len(peaks_list) > 0:
            plt.scatter(
                x[peaks_list],
                y_smooth[peaks_list],
                s=25,
                zorder=5,
            )

    plt.xlabel("Voltage / V")
    plt.ylabel("d²I/dU²")
    plt.title(f"LSV sensitivity overlay - Step {step}, Loop {loop1}")
    plt.legend()
    #plt.tight_layout()

    output_path = output_dir / f"{file_path.stem}_step_{step}_{loop1}_sensitivity_overlay_d2LSV.png"
    plt.savefig(output_path, dpi=300)

    if show_plots:
        plt.show()

    plt.close()


# ========================================================
# Hilfsfunktion Overlay Plots
# ========================================================

def plot_overlay(overlay_plots_data: list, output_dir: Path, show_plot: bool, overlay_plot_name: str):

    for index, dataset in enumerate(overlay_plots_data):
        print(
            index,
            repr(dataset["task"]),
            type(dataset["task"]),
            repr(dataset["segment"]),
        )

    # =============== Test ob alle task gleich sind ================

    tasks = {
        dataset["task"]
        for dataset in overlay_plots_data
    }

    if len(tasks) != 1:
        raise ValueError(
            "Overlay data contains multiple or zero tasks: "
            f"{sorted(tasks)}"
        )

    # ================== Figure erzeugen ======================

    plt.figure(figsize=[8 * 1.1, 5 * 1.1])

    # =============== Einzelne Plots erstellen ================

    for run in overlay_plots_data:
        step = run["step"]
        task = run["task"]
        loop1 = run["loop1"]
        segment = run["segment"]
        voltage = run["voltage"]
        current = run["current"]
        x_values = run["x_values"]
        y_values = run["y_values"]
        x_label = run["x_label"]
        y_label = run["y_label"]

        step_label = step.replace("task_", "Step ")

        if  task == "CV" or task == "PEIS":
            plt.plot(x_values, y_values, label=f"Step {step_label} - {task} - loop {loop1:.0f} at {voltage_number(voltage)}")
        elif task == "GEIS" or task == "CC":
            plt.plot(x_values, y_values, label=f"Step {step_label} - {task} - loop {loop1:.0f} at {current_number(current)}")
        else:
            plt.plot(x_values, y_values, label=f"{step_label} - {task} - loop {loop1}")

        # =============== Labels erstellen ================

        # X Labels
        plt.xlabel(x_label, fontsize=14, labelpad=10)

        # Y Labels
        if task == "CV" or (task == "PEIS" and segment == "hold"):
            voltage_label = voltage.iloc[0]
            plt.ylabel("I / A at" + f"{voltage_number(voltage_label)}", fontsize=14, labelpad=8)

        elif task == "CC" or (task == "GEIS" and segment == "hold"):
            current_label = current.iloc[0]
            plt.ylabel("U /V at" + f"{current_number(current_label)}", fontsize=14, labelpad=8)
        else: # VS sollte unter else fallen
            plt.ylabel(y_label, fontsize=14, labelpad=8)

    # ============== Plot Gerüst erstellen ===================

    plt.legend()
    plt.grid(True, alpha=0.3)

    # ================ Figure speichern ======================

    if task == "VS" and y_label != "I /A":
        overlay_plot_name = overlay_plot_name + "_LSV_1st_diff"

    plot_dir = output_dir / "Overlay Plots"
    plot_dir.mkdir(parents=True, exist_ok=True)
    plot_path = plot_dir / f"{overlay_plot_name}.png"

    # plt.tight_layout() -> nicht verwendet, da ohne padding nicht mehr symmetrisch

    plt.savefig(plot_path, dpi=300)

    if show_plot:
        plt.show()

    plt.close()




# ========================================================
# Hilfsfunktionen Overlay LSV Diff2
# ========================================================

def overlay_diff_lsv_plot_2nd(overlay_plots_diff2: list, output_dir: Path, show_plot: bool, overlay_plot_name: str):

    # =============== Test ob alle task gleich sind ================

    tasks = {
        dataset["task"]
        for dataset in overlay_plots_diff2
    }

    if len(tasks) != 1:
        raise ValueError(
            "Overlay data contains multiple tasks: "
            f"{sorted(tasks)}"
        )

    # ================== Figure erzeugen ======================

    plt.figure(figsize=[8 * 1.1, 5 * 1.1])

    # =============== Einzelne Plots erstellen ================

    for run in overlay_plots_diff2:
        step = run["step"]
        task = run["task"]
        loop1 = run["loop1"]
        segment = run["segment"]
        voltage = run["voltage"]
        current = run["current"]
        x_values = run["x_values"]
        y_values = run["y_values"]
        x_label = run["x_label"]
        y_label = run["y_label"]
        y_savgol = run["y_savgol"]
        peaks_list = run["peaks_list"]
        peak_width_markers = run["peak_width_markers"]

        step_label = step.replace("task_", "Step ")


        plt.plot(x_values, y_values, label=f"{step_label} {loop1:.0f} - LSV 2nd Diff", zorder=1)
        plt.plot(x_values, y_savgol, label=f"{step_label} {loop1:.0f}- smoothed (SG)", zorder=2)

        plt.scatter(
            x_values[peaks_list],  # x-Werte der Peaks
            y_savgol[peaks_list],  # y-Werte der Peaks
            marker="x",
            color = "r",
            label="detected peaks",
            zorder=3
        )
        for marker_data in peak_width_markers:
            peak_width_rel_heights = marker_data["peak_width_rel_heights"]
            left_voltages = marker_data["left_voltages"]
            right_voltages = marker_data["right_voltages"]
            width_heights = marker_data["width_heights"]

            plt.scatter(
                left_voltages,
                width_heights,
                marker="|",
                s=200,
                color = "r",
                label=f"width limits, peak_width_rel_heights={peak_width_rel_heights}",
                zorder=8
            )

            plt.scatter(
                right_voltages,
                width_heights,
                marker="|",
                s=200,
                color = "r",
                zorder=8
            )

    # =============== Labels erstellen ================

    plt.xlabel("Voltage / V", fontsize=14, labelpad=10)
    plt.ylabel(r"$\mathrm{d}^2 I / \mathrm{d}U^2$ / A V$^{-2}$", fontsize=14, labelpad=8)


    # ============== Plot Gerüst erstellen ===================

    plt.legend()
    plt.grid(True, alpha=0.3)

    # ================ Figure speichern ======================

    overlay_plot_name = overlay_plot_name + "_LSV_2nd_diff"

    plot_dir = output_dir / "Overlay Plots"
    plot_dir.mkdir(parents=True, exist_ok=True)
    plot_path = plot_dir / f"{overlay_plot_name}.png"

    # plt.tight_layout() -> nicht verwendet, da ohne padding nicht mehr symmetrisch

    plt.savefig(plot_path, dpi=300)

    if show_plot:
        plt.show()

    plt.close()

# ========================================================
# Hilfsfunktionen: Plot-Modifications
# ========================================================

def voltage_number(voltages: pd.Series):
    return f" {voltages.iloc[2]:.2f}".rstrip("0").rstrip(".") + " V" # Index 2, um Fehler bei 0-1 abzusichern

def current_number(currents: pd.Series):
    return f" {currents.iloc[2]:.2f}".rstrip("0").rstrip(".") + " A" # Index 2, um Fehler bei 0-1 abzusichern

# ========================================================
# Hilfsfunktionen: Standard-Plots
# ========================================================

def cv_plot(times: pd.Series, voltages: pd.Series, currents: pd.Series, file_path: Path, output_dir: Path, step: pd.Series, show_plot: bool, loop1):
    step_label = step.replace("task_", "Step ")
    plt.figure(figsize=[8*1.1,5*1.1])
    plt.plot(times, currents, label = f"{step_label} - CV")
    plt.legend()
    plt.xlabel("Time / s", fontsize = 14, labelpad = 10)
    plt.ylabel("I / A at" + f"{voltage_number(voltages)}", fontsize = 14, labelpad = 8)
    plt.grid(True, alpha=0.3)
    if pd.isna(loop1) or loop1 == "":
        plot_path = output_dir / f"{file_path.stem}_CV.png"
    else:
        plot_dir = output_dir / f"Loop_{loop1:.0f}"
        plot_dir.mkdir(parents=True, exist_ok=True)
        plot_path = plot_dir / f"{file_path.stem}_{step_label}_{loop1:.0f}_CV.png"

    # plt.tight_layout() -> nicht verwendet, da ohne padding nicht mehr symmetrisch
    plt.savefig(plot_path , dpi = 300)
    if show_plot:
        plt.show()
    plt.close()

def peis_hold(times: pd.Series, voltages: pd.Series, currents: pd.Series, file_path: Path, output_dir: Path,
            step: pd.Series, show_plot: bool, loop1):
    step_label = step.replace("task_", "Step ")
    plt.figure(figsize=[8 * 1.1, 5 * 1.1])
    plt.plot(times, currents, label=f"{step_label} - PEIS Hold")
    plt.legend()
    plt.xlabel("Time / s", fontsize=14, labelpad=10)
    plt.ylabel("I / A at" + f"{voltage_number(voltages)}", fontsize=14, labelpad=8)
    plt.grid(True, alpha=0.3)
    if pd.isna(loop1) or loop1 == "":
        plot_path = output_dir / f"{file_path.stem}_CV.png"
    else:
        plot_dir = output_dir / f"Loop_{loop1:.0f}"
        plot_dir.mkdir(parents=True, exist_ok=True)
        plot_path = plot_dir / f"{file_path.stem}_{step_label}_{loop1:.0f}_CV.png"

    # plt.tight_layout() -> nicht verwendet, da ohne padding nicht mehr symmetrisch
    plt.savefig(plot_path, dpi=300)
    if show_plot:
        plt.show()
    plt.close()

def cc_plot(times: pd.Series, voltages: pd.Series, currents: pd.Series, file_path: Path, output_dir: Path,
            step: pd.Series, show_plot: bool, loop1):
    step_label = step.replace("task_", "Step ")
    plt.figure(figsize=[8 * 1.1, 5 * 1.1])
    plt.plot(times, voltages, label=f"{step_label} - CV")
    plt.legend()
    plt.xlabel("Time / s", fontsize=14, labelpad=10)
    plt.ylabel("U / V at" + f"{current_number(currents)}", fontsize=14, labelpad=8)
    plt.grid(True, alpha=0.3)
    if pd.isna(loop1) or loop1 == "":
        plot_path = output_dir / f"{file_path.stem}_CV.png"
    else:
        plot_dir = output_dir / f"Loop_{loop1:.0f}"
        plot_dir.mkdir(parents=True, exist_ok=True)
        plot_path = plot_dir / f"{file_path.stem}_{step_label}_{loop1:.0f}_CV.png"

    # plt.tight_layout() -> nicht verwendet, da ohne padding nicht mehr symmetrisch
    plt.savefig(plot_path, dpi=300)
    if show_plot:
        plt.show()
    plt.close()

def geis_hold(times: pd.Series, voltages: pd.Series, currents: pd.Series, file_path: Path, output_dir: Path,
            step: pd.Series, show_plot: bool, loop1):
    step_label = step.replace("task_", "Step ")
    plt.figure(figsize=[8 * 1.1, 5 * 1.1])
    plt.plot(times, voltages, label=f"{step_label} - GEIS Hold")
    plt.legend()
    plt.xlabel("Time / s", fontsize=14, labelpad=10)
    plt.ylabel("U / V at" + f"{current_number(currents)}", fontsize=14, labelpad=8)
    plt.grid(True, alpha=0.3)
    if pd.isna(loop1) or loop1 == "":
        plot_path = output_dir / f"{file_path.stem}_CV.png"
    else:
        plot_dir = output_dir / f"Loop_{loop1:.0f}"
        plot_dir.mkdir(parents=True, exist_ok=True)
        plot_path = plot_dir / f"{file_path.stem}_{step_label}_{loop1:.0f}_CV.png"

    # plt.tight_layout() -> nicht verwendet, da ohne padding nicht mehr symmetrisch
    plt.savefig(plot_path, dpi=300)
    if show_plot:
        plt.show()
    plt.close()

def lsv_plot(voltages: pd.Series, currents: pd.Series, file_path: Path, output_dir: Path, step: pd.Series, show_plot: bool, loop1):
    step_label = step.replace("task_", "Step ")
    plt.figure(figsize=[6.4*1.3,4.8*1.3])
    plt.plot(voltages, currents, label = f"{step_label} - LSV")
    plt.legend()
    plt.xlabel("U / V", fontsize = 14, labelpad = 10)
    plt.ylabel("I / A", fontsize = 14, labelpad = 8)
    plt.grid(True, alpha=0.3)
    if pd.isna(loop1) or loop1 == "":
        plot_path = output_dir / f"{file_path.stem}_LSV.png"
    else:
        plot_dir = output_dir / f"Loop_{loop1:.0f}"
        plot_dir.mkdir(parents=True, exist_ok=True)
        plot_path = plot_dir / f"{file_path.stem}_{step_label}_{loop1:.0f}_LSV.png"
    # plt.tight_layout() -> nicht verwendet, da ohne padding nicht mehr symmetrisch
    plt.savefig(plot_path , dpi = 300)
    if show_plot:
        plt.show()
    plt.close()

def diff_lsv_plot(voltages: pd.Series, diff_currents: pd.Series, file_path: Path, output_dir: Path, step: pd.Series, show_plot: bool, loop1):
    step_label = step.replace("task_", "Step ")
    plt.figure(figsize=[6.4 * 1.3, 4.8 * 1.3])
    plt.plot(voltages, diff_currents, label=f"{step_label} - LSV")
    plt.legend()
    plt.xlabel("Voltage /V", fontsize=14, labelpad=10)
    plt.ylabel("dI/dU / A V$^{-1}$", fontsize=14, labelpad=8)
    plt.grid(True, alpha=0.3)
    if pd.isna(loop1) or loop1 == "":
        plot_path = output_dir / f"{file_path.stem}_dLSV.png"
    else:
        plot_dir = output_dir / f"Loop_{loop1:.0f}"
        plot_dir.mkdir(parents=True, exist_ok=True)
        plot_path = plot_dir / f"{file_path.stem}_{step_label}_{loop1:.0f}_dLSV.png"
    # plt.tight_layout() -> nicht verwendet, da ohne padding nicht mehr symmetrisch
    plt.savefig(plot_path, dpi=300)
    if show_plot:
        plt.show()
    plt.close()

def diff_lsv_plot_2nd(voltage_valid, diff_2nd_valid, file_path: Path, output_dir: Path, step: pd.Series,
                  show_plot: bool, loop1, diff_2nd_savgol,peaks_list, peak_width_markers):
    step_label = step.replace("task_", "Step ")
    plt.figure(figsize=[6.4 * 1.3, 4.8 * 1.3])
    plt.plot(voltage_valid, diff_2nd_valid, label=f"{step_label} - LSV 2nd Diff", zorder=1)
    plt.plot(voltage_valid, diff_2nd_savgol, label=f"{step_label} - smoothed (SG)", zorder=2)
    plt.scatter(
        voltage_valid.iloc[peaks_list],  # x-Werte der Peaks
        diff_2nd_savgol[peaks_list],  # y-Werte der Peaks
        marker="x",
        color = "r",
        label="detected peaks",
        zorder=3
    )
    for marker_data in peak_width_markers:
        peak_width_rel_heights = marker_data["peak_width_rel_heights"]
        left_voltages = marker_data["left_voltages"]
        right_voltages = marker_data["right_voltages"]
        width_heights = marker_data["width_heights"]

        plt.scatter(
            left_voltages,
            width_heights,
            marker="|",
            s=200,
            color = "r",
            label=f"width limits, peak_width_rel_heights={peak_width_rel_heights}",
            zorder=8
        )

        plt.scatter(
            right_voltages,
            width_heights,
            marker="|",
            s=200,
            color = "r",
            zorder=8
        )

    plt.legend()
    plt.xlabel("Voltage / V", fontsize=14, labelpad=10)
    plt.ylabel(r"$\mathrm{d}^2 I / \mathrm{d}U^2$ / A V$^{-2}$", fontsize=14, labelpad=8)
    plt.grid(True, alpha=0.3)
    if pd.isna(loop1) or loop1 == "":
        plot_path = output_dir / f"{file_path.stem}_d2LSV.png"
    else:
        plot_dir = output_dir / f"Loop_{loop1:.0f}"
        plot_dir.mkdir(parents=True, exist_ok=True)
        plot_path = plot_dir / f"{file_path.stem}_{step_label}_{loop1:.0f}_d2LSV.png"
    # plt.tight_layout() -> nicht verwendet, da ohne padding nicht mehr symmetrisch
    plt.savefig(plot_path, dpi=300)
    if show_plot:
        plt.show()
    plt.close()

def peis_nyquist(real_impedance: pd.Series, imaginary_impedance: pd.Series, file_path: Path, output_dir: Path, step: pd.Series, show_plot: bool, loop1, voltages):
    step_label = step.replace("task_", "Step ")
    plt.figure(figsize=[6.4*1.3,4.8*1.3])
    plt.plot(real_impedance, imaginary_impedance, label = f"Step {step_label} - PEIS at {voltage_number(voltages)}")
    plt.legend()
    plt.xlabel("Re / Ohm", fontsize = 14, labelpad = 10)
    plt.ylabel("-Im / Ohm", fontsize = 14, labelpad = 8)
    plt.grid(True, alpha=0.3)
    if pd.isna(loop1) or loop1 == "":
        plot_path = output_dir / f"{file_path.stem}_PEIS.png"
    else:
        plot_dir = output_dir / f"Loop_{loop1:.0f}"
        plot_dir.mkdir(parents=True, exist_ok=True)
        plot_path = plot_dir / f"{file_path.stem}_{step_label}_{loop1:.0f}_PEIS.png"
    # plt.tight_layout() -> nicht verwendet, da ohne padding nicht mehr symmetrisch
    plt.savefig(plot_path , dpi = 300)
    if show_plot:
        plt.show()
    plt.close()


def geis_nyquist(real_impedance: pd.Series, imaginary_impedance: pd.Series, file_path: Path, output_dir: Path, step: pd.Series, show_plot: bool, loop1, currents):
    step_label = step.replace("task_", "Step ")
    plt.figure(figsize=[6.4*1.3,4.8*1.3])
    plt.plot(real_impedance, imaginary_impedance, label = f"{step_label} - GEIS at {current_number(currents)}")
    plt.legend()
    plt.xlabel("Re / Ohm", fontsize = 14, labelpad = 10)
    plt.ylabel("-Im / Ohm", fontsize = 14, labelpad = 8)
    plt.grid(True, alpha=0.3)
    if pd.isna(loop1) or loop1 == "":
        plot_path = output_dir / f"{file_path.stem}_GEIS.png"
    else:
        plot_dir = output_dir / f"Loop_{loop1:.0f}"
        plot_dir.mkdir(parents=True, exist_ok=True)
        plot_path = plot_dir / f"{file_path.stem}_{step_label}_{loop1:.0f}_GEIS.png"
    # plt.tight_layout() -> nicht verwendet, da ohne padding nicht mehr symmetrisch
    plt.savefig(plot_path , dpi = 300)
    if show_plot:
        plt.show()
    plt.close()


# ========================================================
# Hauptfunktion Start
# ========================================================

def plot_corrected(
        input_folder: Path,
        output_folder: Path,
        show_plots,
        lsv_extended,
        current_smoothing_1st_derivative,
        current_smoothing_2nd_derivative,
        derivative_smoothing_2nd_derivative,
        bucket_width,
        savgol_window_points,
        prominence,
        smoothing_method,
        min_feature_size,
        lsv_sensitivity_plots=False,
        lsv_sensitivity_analysis=False,
        lsv_sensitivity_configs=None,
        lsv_sensitivity_overlay_plots=False,
        peak_width_rel_heights=(0.2, 0.5, 0.8, 0.95),
        plot_peak_width_rel_height=0.5,
        overlay_plots=False,
        overlay_plots_dict=None,
        overlay_plot_name="overlay_plot",
        lsv_linear_fit=False,
        fit_start_voltage=2.3,
        fit_end_voltage=2.5,
        ):

    if lsv_sensitivity_configs is None:
        lsv_sensitivity_configs = []

    lsv_sensitivity_data = []
    overlay_plots_data = []
    overlay_plots_diff1 = []
    overlay_plots_diff2 = []

    # ========================================================
    # File Handling
    # ========================================================

    input_dir = Path(input_folder)
    if not input_dir.is_dir():
        exit("Input directory does not exist")

    # Output Ordner definieren

    output_dir = Path(output_folder)
    output_dir.mkdir(exist_ok=True)

    # Dokumentation erstellen plot dict

    plot_results = {}
    lsv_lines_cut = {}
    eis_hold_values = {}
    peak_widths_data = []
    lsv_sensitivity_peak_data = []

    create_lsv_diff_overlays = (
            overlay_plots
            and lsv_extended
            and "VS" in overlay_plots_dict["task"]
    )

    # File öffnen, Output Path kommt ggf. später dazu - Dataframe erstellen

    for file_path in input_dir.glob("*.csv"):
        df = pd.read_csv(file_path)

        # ========================================================
        # df.Series Metadaten erzeugen
        # ========================================================

        # Measurement_id für Doku definieren
        measurement_id = (df["Step"].iloc[0], df["Task"].iloc[0], df["Loop 1 number"].iloc[0], df["Segment"].iloc[0])
        method = df["Task"].iloc[0]
        loop1 = df["Loop 1 number"].iloc[0] #brauchen wir für Aufteilung in Ordner
        segment = df["Segment"].iloc[0]
        step = df["Step"].iloc[0]
        task = df["Task"].iloc[0]


        # ========================================================
        # LSV cleanup
        # ========================================================

        if method == "VS": # for LSV evaluation: U should only be increasing - thus we remove non-increasing values
            df = df.reset_index(drop=True)

            delta_v = df["U /V"].diff()
            falling_or_equal = delta_v.iloc[1:] <= 0

            bad_points = falling_or_equal[falling_or_equal] # Boolean mask: True where voltage no longer increases
            # Hier können Theoretisch zu früh Werte abgeschnitten werden, auf Documentary achten!
            if len(bad_points) > 0:
                first_bad_index = bad_points.index[0]
                rows_before = len(df)
                df = df.iloc[:first_bad_index] # hier wird tatsächlich geschnitten
                lsv_lines_cut[measurement_id] = rows_before - len(df)
            else:
                lsv_lines_cut[measurement_id] = 0

        # ========================================================
        # df.Series für Auswertung erzeugen
        # ========================================================

        time = df["Time /s"]
        voltage = df["U /V"]
        current = df["I /A"]
        frequency = df["Frequency /Hz"]
        impedance_module = df["Impedance module /Ohms"]
        impedance_phase = df["Impedance phase /rad"]
        real_impedance = df["Real impedance /Ohms"]
        imaginary_impedance = df["- Imaginary impedance /Ohms"]

        # ========================================================
        # LSV Extended
        # ========================================================

        if method == "VS" and lsv_extended:

            function_peak_data, lsv_plot_data = lsv_differentials(smoothing_method,
                      current_smoothing_1st_derivative,
                      current_smoothing_2nd_derivative,
                      derivative_smoothing_2nd_derivative,
                      savgol_window_points,
                      df,
                      bucket_width,
                      min_feature_size,
                      prominence,
                      peak_width_rel_heights,
                      plot_peak_width_rel_height
                      )


            # Return Peakbreiten für Dokumentation
            peak_widths_data.extend(function_peak_data)

            # ========================================================
            # LSV Sensitivity Analyse
            # ========================================================

            if lsv_sensitivity_analysis:
                sensitivity_output_dir = output_dir / "LSV_sensitivity"
                sensitivity_output_dir.mkdir(parents=True, exist_ok=True)

                sensitivity_runs = []

                for config in lsv_sensitivity_configs:
                    sensitivity_peak_data, sensitivity_plot_data = lsv_differentials(
                        config["smoothing_method"],
                        config["current_smoothing_1st_derivative"],
                        config["current_smoothing_2nd_derivative"],
                        config["derivative_smoothing_2nd_derivative"],
                        config["savgol_window_points"],
                        df,
                        config["bucket_width"],
                        config["min_feature_size"],
                        config["prominence"],
                        config["peak_width_rel_heights"],
                        config["plot_peak_width_rel_height"]
                    )

                    for row in sensitivity_peak_data:
                        row["Sensitivity label"] = config["label"]
                        row["Sensitivity smoothing method"] = config["smoothing_method"]
                        row["current_smoothing_1st_derivative"] = config["current_smoothing_1st_derivative"]
                        row["current_smoothing_2nd_derivative"] = config["current_smoothing_2nd_derivative"]
                        row["derivative_smoothing_2nd_derivative"] = config["derivative_smoothing_2nd_derivative"]
                        row["savgol_window_points"] = config["savgol_window_points"]
                        row["prominence"] = config["prominence"]
                        row["min_feature_size"] = config["min_feature_size"]
                        row["plot_peak_width_rel_height"] = config["plot_peak_width_rel_height"]
                        row["peak_width_rel_heights"] = str(config["peak_width_rel_heights"])

                    lsv_sensitivity_peak_data.extend(sensitivity_peak_data)


                    # ===========   Für Overlay Plot sammeln   ================
                    sensitivity_runs.append({
                        "label": config["label"],
                        "plot_data": sensitivity_plot_data,
                        "config": config,
                    })

                    # ========================================================
                    # LSV Sensitivity Plots
                    # ========================================================

                    if lsv_sensitivity_plots:
                        config_output_dir = sensitivity_output_dir / config["label"]
                        config_output_dir.mkdir(parents=True, exist_ok=True)

                        if config["smoothing_method"] == "rolling":
                            diff_lsv_plot(
                                voltage,
                                sensitivity_plot_data["lsv_derivative_1st"],
                                file_path,
                                config_output_dir,
                                step,
                                show_plots,
                                loop1,
                            )

                            diff_lsv_plot_2nd(
                                sensitivity_plot_data["voltage_valid"],
                                sensitivity_plot_data["diff_2nd_valid"],
                                file_path,
                                config_output_dir,
                                step,
                                show_plots,
                                loop1,
                                sensitivity_plot_data["diff_2nd_savgol"],
                                sensitivity_plot_data["peaks_list"],
                                sensitivity_plot_data["peak_width_markers"],
                            )

                        else:
                            diff_lsv_plot(
                                sensitivity_plot_data["voltage_buckets"],
                                sensitivity_plot_data["lsv_bucket_derivative_1st"],
                                file_path,
                                config_output_dir,
                                step,
                                show_plots,
                                loop1,
                            )

                            diff_lsv_plot_2nd(
                                sensitivity_plot_data["bucket_voltage_valid"],
                                sensitivity_plot_data["bucket_diff_2nd_valid"],
                                file_path,
                                config_output_dir,
                                step,
                                show_plots,
                                loop1,
                                sensitivity_plot_data["diff_2nd_savgol"],
                                sensitivity_plot_data["peaks_list"],
                                sensitivity_plot_data["peak_width_markers"],
                            )

                if lsv_sensitivity_overlay_plots and len(sensitivity_runs) > 0:

                    overlay_output_dir = sensitivity_output_dir / "overlay"
                    overlay_output_dir.mkdir(parents=True, exist_ok=True)

                    plot_lsv_sensitivity_overlay_2nd(
                        sensitivity_runs=sensitivity_runs,
                        file_path=file_path,
                        output_dir=overlay_output_dir,
                        step=step,
                        loop1=loop1,
                        show_plots=show_plots,
                    )

                    plot_lsv_sensitivity_overlay_1st(
                        sensitivity_runs=sensitivity_runs,
                        file_path=file_path,
                        output_dir=overlay_output_dir,
                        step=step,
                        loop1=loop1,
                        show_plots=show_plots,
                    )

        # ========================================================
        # Daten für Overlay Abspeichern
        # ========================================================

        overlay_combinations = set(zip(
            overlay_plots_dict["step"],
            overlay_plots_dict["task"],
            overlay_plots_dict["loop"],
            overlay_plots_dict["segment"],
        ))

        current_combination = (step, task, loop1, segment)

        print("Gesucht:", overlay_combinations)
        print("Aktuell:", current_combination)
        print("Treffer:", current_combination in overlay_combinations)

        base_name = file_path.stem.split("_task_", 1)[0]

        if overlay_plots and current_combination in overlay_combinations:

            if task == "CV" or (task == "PEIS" and segment == "hold"):
                x_values = time
                y_values = current
                x_label = "Time /s"
                y_label = "I /A"

            elif task == "CC" or (task == "GEIS" and segment == "hold"):
                x_values = time
                y_values = voltage
                x_label = "Time /s"
                y_label = "U /V"

            elif task == "VS":
                x_values = voltage
                y_values = current
                x_label = "U /V"
                y_label = "I /A"

            elif task in ("PEIS", "GEIS") and segment == "eis":
                x_values = real_impedance
                y_values = imaginary_impedance
                x_label = "Re /Ohm"
                y_label = "- Im /Ohm"

            else:
                raise ValueError(
                    f"Overlay plotting is not implemented for "
                    f"task={task}, segment={segment}."
                )

            valid_values = x_values.notna() & y_values.notna()

            if not valid_values.any():
                raise ValueError(
                    f"No valid overlay data found for "
                    f"step={step}, task={task}, loop={loop1}, segment={segment}."
                )

            overlay_plots_data.append({
                "base_name": base_name,
                "step": step,
                "task": task,
                "loop1": loop1,
                "segment": segment,
                "x_values": x_values[valid_values].copy(),
                "y_values": y_values[valid_values].copy(),
                "x_label": x_label,
                "y_label": y_label,
                "voltage": voltage,
                "current": current,
            })

            if create_lsv_diff_overlays and task == "VS":

                if smoothing_method == "rolling":
                    x_values = voltage
                    y_values = lsv_plot_data["lsv_derivative_1st"]
                else:
                    x_values = lsv_plot_data["voltage_buckets"]
                    y_values = lsv_plot_data["lsv_bucket_derivative_1st"]

                x_label = "U /V"
                y_label = "dI/dU / A V$^{-1}$"

                overlay_plots_diff1.append({
                    "base_name": base_name,
                    "step": step,
                    "task": task,
                    "loop1": loop1,
                    "segment": segment,
                    "x_values": x_values[valid_values].copy(),
                    "y_values": y_values[valid_values].copy(),
                    "x_label": x_label,
                    "y_label": y_label,
                })

                if smoothing_method == "rolling":
                    x_values = lsv_plot_data["voltage_valid"]
                    y_values = lsv_plot_data["diff_2nd_valid"]
                else:
                    x_values = lsv_plot_data["bucket_voltage_valid"]
                    y_values = lsv_plot_data["bucket_diff_2nd_valid"]

                x_label = "U /V"
                y_label = "dI/dU / A V$^{-1}$"

                overlay_plots_diff2.append({
                    "base_name": base_name,
                    "step": step,
                    "task": task,
                    "loop1": loop1,
                    "segment": segment,
                    "x_values": x_values[valid_values].copy(),
                    "y_values": y_values[valid_values].copy(),
                    "x_label": x_label,
                    "y_label": y_label,
                    "y_savgol": lsv_plot_data["diff_2nd_savgol"],
                    "peaks_list": lsv_plot_data["peaks_list"],
                    "peak_width_markers": lsv_plot_data["peak_width_markers"],
                })


        # ========================================================
        # Nach Methode Plotfunktionen aufrufen
        # ========================================================

        if method == "REST":
            plot_results[measurement_id] = "skipped" # Rest is not evaluated thus skipped
            continue

        elif method == "CV": # OPTIONAL: einen Steigungsdeckel einzubauen um automatisch Steigungen auszuwerten!
            plot_results[measurement_id] = "plot saved"
            cv_plot(time, voltage, current, file_path, output_dir, step, show_plots,loop1)


        elif method == "PEIS":
            if segment == "hold":
                plot_results[measurement_id] = "plot saved"
                peis_hold(time, voltage, current, file_path, output_dir, step, show_plots, loop1)
                if not df.empty:
                    eis_hold_values[measurement_id] = voltage.iloc[-1], current.iloc[-1]
                else:
                    eis_hold_values[measurement_id] = math.nan, math.nan
            elif segment == "eis":
                plot_results[measurement_id] = "plot saved"
                peis_nyquist(real_impedance, imaginary_impedance, file_path, output_dir, step, show_plots,loop1, voltage)
        elif method == "GEIS":
            if segment == "hold":
                plot_results[measurement_id] = "plot saved"
                geis_hold(time, voltage, current, file_path, output_dir, step, show_plots, loop1)
                if not df.empty:
                    eis_hold_values[measurement_id] = voltage.iloc[-1], current.iloc[-1]
                else:
                    eis_hold_values[measurement_id] = math.nan, math.nan
            elif segment == "eis":
                plot_results[measurement_id] = "plot saved"
                geis_nyquist(real_impedance, imaginary_impedance, file_path, output_dir, step, show_plots,loop1, current)

        elif method == "VS":
            plot_results[measurement_id] = "plot saved"
            lsv_plot(voltage, current, file_path, output_dir, step, show_plots,loop1)
            if lsv_extended:
                if smoothing_method == "rolling":
                    diff_lsv_plot(voltage, lsv_plot_data["lsv_derivative_1st"], file_path, output_dir, step, show_plots,loop1)
                    diff_lsv_plot_2nd(lsv_plot_data["voltage_valid"], lsv_plot_data["diff_2nd_valid"], file_path, output_dir, step, show_plots, loop1,lsv_plot_data["diff_2nd_savgol"],lsv_plot_data["peaks_list"],lsv_plot_data["peak_width_markers"])
                else:
                    diff_lsv_plot(lsv_plot_data["voltage_buckets"], lsv_plot_data["lsv_bucket_derivative_1st"], file_path, output_dir, step, show_plots, loop1)
                    diff_lsv_plot_2nd(lsv_plot_data["bucket_voltage_valid"], lsv_plot_data["bucket_diff_2nd_valid"], file_path, output_dir, step, show_plots, loop1,
                                      lsv_plot_data["diff_2nd_savgol"], lsv_plot_data["peaks_list"], lsv_plot_data["peak_width_markers"])

        else:
            plot_results[measurement_id] = "method not implemented"

    # ========================================================
    # Cleanup nach der Schleife - Peakdaten, Overlay Plot erzeugen, Return
    # ========================================================

    width_df = pd.DataFrame(peak_widths_data)

    if overlay_plots:

        # Aufruf der allgemeinen Overlay Plot funktion
        plot_overlay(overlay_plots_data, output_dir, show_plots, overlay_plot_name)

        requested_tasks = overlay_plots_dict["task"]

        if create_lsv_diff_overlays:

            # Aufruf diff 1 Funktion
            plot_overlay(overlay_plots_diff1, output_dir, show_plots, overlay_plot_name)

            # Aufruf diff 2 Funktion
            plot_overlay(overlay_plots_diff2, output_dir, show_plots, overlay_plot_name)

    return plot_results, lsv_lines_cut, eis_hold_values, width_df
