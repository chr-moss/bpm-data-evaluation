from pathlib import Path
import pandas as pd
import settings


# ========================================================
# HILFSFUNKTIONEN
# ========================================================


def round_tolerance(value):

    # Value ist I oder U je nach Methode
    step_size = settings.step_size
    tolerance = settings.step_tolerance

    target = round(value / step_size) * step_size

    if abs(value - target) <= tolerance:
        value = target

    return value

def format_frequency(freq):

    if freq >= 1e6:
        value = freq / 1e6
        unit = "MHz"

    elif freq >= 1e3:
        value = freq / 1e3
        unit = "kHz"

    else:
        value = freq
        unit = "Hz"

    rounded = float(f"{value:.1g}")

    return f"{rounded:g} {unit}" # :g heißt Autoformat durch Python

def describe_measurement(row):

    # Constant Voltage (CV) soll die Spannung zeigen
    if row["Task"] == "CV":
        return f'U: {round_tolerance(row["Last_U"]):.{settings.round_decimals}f} V'

    # Constant Current (CC) soll den Strom zeigen
    elif row["Task"] == "CC":
        return f'U: {round_tolerance(row["Last_I"]):.{settings.round_decimals}f} A'

    # LSV soll Spannungsbereich zeigen
    elif row["Task"] == "VS":
        return f'U: {round_tolerance(row["First_U"]):.{settings.round_decimals}f} to {round_tolerance(row["Last_U"]):.{settings.round_decimals}f} V'

    # PEIS und GEIS HOLD sollen die Hold-Spannung zeigen
    elif row["Task"] == "PEIS" and row["Segment"] == "hold":
        return f'U: {round_tolerance(row["Last_U"]):.{settings.round_decimals}f} V'

    elif row["Task"] == "GEIS" and row["Segment"] == "hold":
        return f'U: {round_tolerance(row["Last_I"]):.{settings.round_decimals}f} V'

    # PEIS und GEIS EIS sollen Frequenzbereich und Mean zeigen
    elif row["Task"] == "PEIS" and row["Segment"] == "eis":
        return f'U: {round_tolerance(row["Mean_U"]):.{settings.round_decimals}f} V, f: '+format_frequency(row["Min_F"])+ ' to '+format_frequency(row["Max_F"])

    elif row["Task"] == "GEIS" and row["Segment"] == "eis":
        return f'I: {round_tolerance(row["Mean_I"]):.{settings.round_decimals}f} V, f: '+format_frequency(row["Min_F"])+ ' to '+format_frequency(row["Max_F"])

    # Wenn keine bekannte Methode soll die Spalte leer bleiben
    return ""

# ========================================================
# HAUPTFUNKTION
# ========================================================


def measurement_documentation(input_path: Path, output_path: Path):

    # ========================================================
    # File Handling und Vorbereitung
    # ========================================================

    # 1. alle corrected CSVs einlesen

    input_dir = Path(input_path)
    if not input_dir.is_dir():
        exit("Input directory does not exist")
    output_dir = Path(output_path)
    output_dir.mkdir(exist_ok=True)

    # Liste für Dataframes
    dataframes = []

    for file_path in input_dir.glob("*.csv"):
        df = pd.read_csv(file_path)

        # 2. SourceFile-Spalte ergänzen

        df["SourceFile"] = file_path.name

    # ========================================================
    # Daten zusammenfassen und Sortieren
    # ========================================================

        # Liste von Dataframes erstellen
        dataframes.append(df)

    # 3. alle DataFrames mit pd.concat zusammenführen
    # Liste mit concat zusammenführen zu neuem großen Dataframe
    all_data = pd.concat(dataframes)

    all_data["Step number"] = all_data["Step"].str.split("_").str[-1].astype(int)

    # 4. groupby(["Step", "Task"]) Summary erzeugen

    summary = all_data.groupby(
        ["Loop 1 number", "Step number", "Task", "Segment"],
        dropna=False
    ).agg(
        Rows=("Time /s", "count"),
        First_U=("U /V", "first"),
        Last_U=("U /V", "last"),
        Min_U=("U /V", "min"),
        Max_U=("U /V", "max"),
        Mean_U=("U /V", "mean"),
        First_I=("I /A", "first"),
        Last_I=("I /A", "last"),
        Mean_I=("I /A", "mean"),
        Start_time=("Time /s", "first"),
        End_time=("Time /s", "last"),
        Min_F=("Frequency /Hz", "min"),
        Max_F=("Frequency /Hz", "max"),
    ).reset_index()

    # Die Segment Order definieren
    segment_order = {"hold": 0, "eis": 1}

    # die Segment order Spalte wird angelegt mit den Werten 0-2 um Sortierung vorzubereiten
    summary["Segment order"] = summary["Segment"].map(segment_order).fillna(2)

    # Sortierung nach Segment Order
    summary = summary.sort_values(
        by=["Loop 1 number", "Step number", "Task", "Segment order"],
        na_position="first"
    )

    # Hilfsspalte Segment Order wird wieder entfernt
    summary = summary.drop(columns="Segment order").reset_index(drop=True)


    # ========================================================
    # Infospalte erzeugen
    # ========================================================

    summary["Measurement info"] = summary.apply(
        describe_measurement,
        axis=1 # -> heißt für jede Zeile einzeln anwenden
    )

    # ========================================================
    # Zeitspalten erzeugen
    # ========================================================

    summary["Duration /s"] = summary["End_time"] - summary["Start_time"]
    summary["Duration /min"] = summary["Duration /s"]/60
    summary["Duration /h"] = summary["Duration /s"]/3600

    # ========================================================
    # Ausgabespalten auswählen
    # ========================================================

    if settings.time_units == "min":

        output_df = summary[[
            "Loop 1 number",
            "Step number",
            "Task",
            "Segment",
            "Measurement info",
            "Duration /min"
        ]].copy()

    elif settings.time_units == "s":

        output_df = summary[[
            "Loop 1 number",
            "Step number",
            "Task",
            "Segment",
            "Measurement info",
            "Duration /s"
        ]].copy()

    else:

        output_df = summary[[
            "Loop 1 number",
            "Step number",
            "Task",
            "Segment",
            "Measurement info",
            "Duration /h"
        ]].copy()


    # ========================================================
    # Ausgabe bereinigen
    # ========================================================

    # Zeitspalte bereinigen - runden
    if settings.time_units == "min":
        output_df["Duration /min"] = output_df["Duration /min"].round(1)
    elif settings.time_units == "s":
        output_df["Duration /s"] = output_df["Duration /s"].round(1)
    else:
        output_df["Duration /h"] = output_df["Duration /h"].round(1)

    output_df["Loop 1 number"] = (
        output_df["Loop 1 number"]
        .astype("Int64")
        .astype("string")
        .fillna("No Loop")
    )


    # ========================================================
    # Summary als CSV speichern
    # ========================================================

    output_df.to_csv(
        output_dir / "measurement_documentation.csv",
        sep=settings.csv_separator,
        decimal=settings.csv_decimal,
        encoding=settings.csv_encoding,
        index=False
    )

    print()
    print("=================================================================================")
    print("Measurement Documentation:")
    print("=================================================================================")
    print(output_df.to_string(index=False))