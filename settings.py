from pathlib import Path


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
potentiostat = "915"


# ========================================================
# Einstellungen Export
# ========================================================

# =================   CSV general   ======================

# Measurement Documentation - CSV Export
csv_separator = ";"
csv_decimal = ","
csv_encoding = "utf-8-sig"

# ================   DearEis tables   ====================

# ACHTUNG: der Output ist aktuell für die Software DearEis angepasst -> ggf. Format anpassen

# "plot" → nur plotten, kein Export
# "deareis" → keine EIS Plots, nur die Tabellen
# "both" → beides ausgeben

eis_output = "deareis"

# Ausgabe von Excel-Files für LinKK (KIT-Tool für Kramers Kronig)
# Nur aktiv wenn eis_output = deareis oder both

lin_kk = False


# ========================================================
# Einstellungen Measurement documentation
# ========================================================


# Wie groß ist der Abstand der erwarteten Stepgröße (in V oder A)
step_size = 0.05

# Wie groß ist die Toleranz für die Rundung auf diese Steps (in V oder A)
step_tolerance = 0.01

# Auf wie viele Stellen soll die Ausgabe von Strom/Spannung gerundet werden?
round_decimals = 2

# Welche Zeiteinheit soll angezeigt werden (s, min, h)
time_units = "min"


# ========================================================
# Einstellungen Plots
# ========================================================


# =================   Show Plots?   ======================

# Sollen Plots als Pop-Up gezeigt werden in Plots?

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

# macht alle Auswertungen jenseits des einfachen Anzeigens vom LSV
# → 1. und 2. Ableitung
# → Smoothing und fit der Ableitungen

lsv_extended = True  # CURRENT LSV NOCH HINZUFÜGEN !


# ==========   Allg. Smoothing Einstellungen   =============

# Mit welcher Smoothing Methode soll geglätted werden?
# → rolling: sehr effektiv aber erzeugt NaN am Anfang
# → bucket: braucht ausreichend Punkte, aber kein NaN

smoothing_method = "rolling"

# Stellt die Empfindlichkeit der Peakerkennung ein
# kleine Prominence → kleine Peaks werden erkannt

prominence = 1.1

# =================   Rolling Mean   ======================

if smoothing_method == "rolling":

    # Rauschunterdrückung: Gibt an über wie viele Punkte gemittelt wird
    # Im Zweifel prüfen wie viele Punkte / mV aufgenommen wurden

    current_smoothing_1st_derivative = 10  # → Glättet den Strom für 1. Ableitung
    current_smoothing_2nd_derivative = 50  # → Glättet den Strom für 2. Ableitung
    derivative_smoothing_2nd_derivative = 120  # → Glättet die 1. Ableitung vor der 2.

# =================   Savgol Filter   ======================

    # Savgol Widnow Points -> wie viele Punkte verwendet der Savgol Filter für Fits
    # WICHTIG:  Point Distance x savgol_window_size MUSS < Feature-Breite sein

    savgol_window_points = 91

    # Bucket Parameters not used (nicht ändern, es muss "None" übergeben werden
    bucket_width = None
    min_feature_size = None
    feature_points = None # TESTEN OB DAS NOCH GEBRAUCHT WIRD

# ===============   Bucket Smoothing   ====================

else:  # Else -> Smoothing Method wird immer "Bucket"

    # Bucket Größe einstellen
    bucket_width = 0.01  # in V

    # Mindestabstand zwischen zwei erkannten Peaks
    min_feature_size = 0.2  # in V

    feature_points = round(min_feature_size / bucket_width)

# =================   Savgol Filter   ======================

    savgol_window_points = max(7, round(min_feature_size / bucket_width / 2))

    if savgol_window_points % 2 == 0:
        savgol_window_points = savgol_window_points + 1
    if savgol_window_points < 7:
        raise ValueError("Not enough savgol window points provided")
    elif 7 <= savgol_window_points < 10:
        print("Savgol window points low, this can be inaccurate")

    # Rolling Parameters not used (nicht ändern, es muss "None" übergeben werden
    current_smoothing_1st_derivative = None
    current_smoothing_2nd_derivative = None
    derivative_smoothing_2nd_derivative = None

# ================   Peak Analysis   ====================

# Auf welchen Höhen werden Peakbreiten analysiert (-> CSV)
peak_width_rel_heights = [0.5, 0.8, 0.95]

# Auf welchen relativen Peakhöhen liegen die Peakmarker in den Plots
plot_peak_width_rel_height = 0.5

# ==========   LSV Sensitivity Analysis   ===============

lsv_sensitivity_plots = False

lsv_sensitivity_analysis = False

lsv_sensitivity_overlay_plots = False

# HIER Parameter für Sensitivitätsanalyse einstellen
# 3 verschiedene, um Einfluss der Methode zu testen

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

# für Kennlinien: "True", für nur Einzelmessungen "False"
evaluate_curves = True

# Sollen Plots der Pop-Up gezeigt werden in "evaluate"?
evaluate_show_plots = False

# ========================================================
# Folders
# ========================================================


raw_input_dir = Path("input")
steps_raw_dir = Path("steps_raw")
steps_corrected_dir = Path("steps_corrected")
plot_dir = Path("plots")
evaluate_dir = Path("evaluation")
export_dir = Path("export")