from pathlib import Path
import pandas as pd
from galvani import BioLogic

#=====================================================
# Hilfsfunktion: Aus Filename Step und Task holen
#=====================================================

def parse_btlab_filename(file_path: Path) -> dict:
    file_path = Path(file_path)
    stem = file_path.stem

    parts = stem.rsplit("_", 3)

    if len(parts) != 4:
        raise ValueError(
            f"Could not parse BT-Lab filename. Expected ending like "
            f"'_03_LSV_CA3', got: {file_path.name}"
        )

    base_name, technique_number_text, technique_name, channel_text = parts

    if not technique_number_text.isdigit():
        raise ValueError(
            f"Could not parse technique number from filename: {file_path.name}"
        )

    return {
        "source_file": file_path.name,
        "base_name": base_name,
        "source_technique_number": int(technique_number_text),
        "source_task": technique_name,
    }


#=====================================================
# Hilfsfunktion: Werte anpassen
#=====================================================

def normalize_values(df: pd.DataFrame, file_path) -> pd.DataFrame:

    # ========== Strom ==========
    if "I /A" in df.columns:
        pass
    elif "<I>/mA" in df.columns:
        df["I /A"] = df["<I>/mA"] / 1000
    elif "I/mA" in df.columns:
        df["I /A"] = df["I/mA"] / 1000
    elif "I/A" in df.columns:
        df["I /A"] = df["I/A"]
    else:
        raise ValueError("No current column found.")

    df["I /A"] = pd.to_numeric(df["I /A"], errors="coerce")

    # ========== Ns =========
    if "Ns" in df.columns:
        df["BTLab Ns"] = df["Ns"]
    else:
        df["BTLab Ns"] = ""

    # ========== Loop1 number (wird weiter unten vervollständigt) =========
    df["Loop 1 number"] = ""

    # ========== Spannung =========
    if "U /V" in df.columns:
        pass
    elif "Ecell/V" in df.columns:
        df["U /V"] = df["Ecell/V"]
    elif "Ewe/V" in df.columns:
        df["U /V"] = df["Ewe/V"]
    else:
        raise ValueError("No voltage column found.")

    df["U /V"] = pd.to_numeric(df["U /V"], errors="coerce")

    # ========== Zeit =========
    if "Time /s" in df.columns:
        pass
    elif "time/s" in df.columns:
        df["Time /s"] = df["time/s"]
    else:
        raise ValueError("No time column found.")

    df["Time /s"] = pd.to_numeric(df["Time /s"], errors="coerce")

    # ========== Cycle number =========
    if "Cycle number" in df.columns:
        pass
    elif "cycle number" in df.columns:
        df["Cycle number"] = df["cycle number"]
    else:
        df["Cycle number"] = "" #Cycle number ist nicht immer nötig daher hier kein Abbruch

    # ========== Step =========
    file_info = parse_btlab_filename(file_path)
    step_number = file_info["source_technique_number"]
    if not step_number:
        raise ValueError(f"Could not parse technique number from filename: {file_path.name}")
    else:
        step = "task_" + str(step_number)
        df["Step"] = step

    # ========== Task =========
    task = file_info["source_task"]
    if task == "LSV":
        df["Task"] = "VS"
    elif task == "CstV":
        df["Task"] = "CV"
    else:
        raise ValueError("No task found or task not implemented.")

    return df

#=====================================================
# Hilfsfunktion: Loops über Zeitsprünge erkennen
#=====================================================

def detect_loop_starts_by_time_jump(
    df: pd.DataFrame,
    time_column: str = "time/s",
    min_loop_time_jump_s: float = 300,
) -> list[int]:
    if time_column not in df.columns:
        raise ValueError(
            f"Time column '{time_column}' not found. "
            f"Available columns: {list(df.columns)}"
        )

    time_values = pd.to_numeric(df[time_column], errors="coerce")

    if time_values.isna().any():
        raise ValueError(
            f"Time column '{time_column}' contains non-numeric or NaN values."
        )

    delta_t = time_values.diff()

    loop_start_indices = delta_t[delta_t > min_loop_time_jump_s].index.tolist() #gib alle indices wo delta_t > min_loop ist

    loop_starts = [0] + loop_start_indices

    return loop_starts

#=====================================================
# Hilfsfunktion: Loop Wert in Dataframe schreiben
#=====================================================

def assign_loop_numbers_from_starts(
    df: pd.DataFrame,
    loop_starts: list[int],
) -> pd.DataFrame:

    df = df.copy() #Absichern, dass nur geändert wird was an Ende returned wird

    loop_starts = sorted(set(int(index) for index in loop_starts))
    # int -> stellt sicher alles in, set -> Erzeugt eine Menge, Doppelte werden entfernt, sorted -> erzeugt sortierte Liste

    loop_starts = [
        index for index in loop_starts
        if 0 <= index < len(df)
    ]

    if 0 not in loop_starts:
        loop_starts.insert(0, 0)

    if len(loop_starts) <= 1:
        df["Loop 1 number"] = ""
        return df

    df["Loop 1 number"] = ""

    for i, start in enumerate(loop_starts):
        if i + 1 < len(loop_starts):
            end = loop_starts[i + 1]
        else:
            end = len(df)

        df.loc[start:end - 1, "Loop 1 number"] = i + 1

    return df

#=====================================================
# Hilfsfunktion: Loop Wert in Dataframe schreiben
#=====================================================

def apply_time_jump_loop_detection(
    df: pd.DataFrame,
    time_column: str = "time/s",
    min_loop_time_jump_s: float = 300,
    min_loop_segment_rows: int = 50,
) -> tuple[pd.DataFrame, dict]:

    loop_starts = detect_loop_starts_by_time_jump(
        df=df,
        time_column=time_column,
        min_loop_time_jump_s=min_loop_time_jump_s,
    )

    df, segment_report = split_by_loop_starts_and_filter_short_segments(
        df=df,
        loop_starts=loop_starts,
        min_loop_segment_rows=min_loop_segment_rows,
    )

    skipped_short_segment_rows = sum(
        segment["rows"]
        for segment in segment_report
        if not segment["kept"]
    )

    loop_info = {
        "loop_source": "heuristic_time_jump",
        "split_confidence": "heuristic",
        "loop_starts": loop_starts,
        "number_of_detected_loop_candidates": len(loop_starts),
        "number_of_kept_segments": sum(
            1 for segment in segment_report
            if segment["kept"]
        ),
        "skipped_short_segment_rows": skipped_short_segment_rows,
        "min_loop_time_jump_s": min_loop_time_jump_s,
        "min_loop_segment_rows": min_loop_segment_rows,
        "segment_report": segment_report,
    }

    return df, loop_info

#=====================================================
# Hilfsfunktion: Zu kurze Loops entfernen
#=====================================================

def split_by_loop_starts_and_filter_short_segments(
    df: pd.DataFrame,
    loop_starts: list[int],
    min_loop_segment_rows: int = 50,
) -> tuple[pd.DataFrame, list[dict]]:

    df = df.copy()

    loop_starts = sorted(set(int(index) for index in loop_starts))

    if 0 not in loop_starts:
        loop_starts.insert(0, 0)

    valid_segments = []
    segment_report = []

    for i, start in enumerate(loop_starts):
        if i + 1 < len(loop_starts):
            end = loop_starts[i + 1]
        else:
            end = len(df)

        segment_length = end - start
        keep_segment = segment_length >= min_loop_segment_rows

        segment_report.append({
            "candidate_loop": i + 1,
            "start": start,
            "end": end,
            "rows": segment_length,
            "kept": keep_segment,
        })

        if keep_segment:
            segment_df = df.iloc[start:end].copy()
            segment_df["Loop 1 number"] = len(valid_segments) + 1
            valid_segments.append(segment_df)

    if len(valid_segments) == 0:
        df["Loop 1 number"] = ""
        return df.iloc[0:0].copy(), segment_report

    df_filtered = pd.concat(valid_segments, ignore_index=True)

    if len(valid_segments) == 1:
        df_filtered["Loop 1 number"] = ""

    return df_filtered, segment_report


#=====================================================
# Hauptfunktion
#=====================================================


def mpr_to_csv(input_folder: Path, output_folder: Path):

    #=====================================================
    # Dateien laden
    #=====================================================

    # ========== Input und Output Path =========
    input_dir = Path(input_folder)

    if not input_dir.is_dir():
        exit("Input directory does not exist")

    output_dir = Path(output_folder)
    output_dir.mkdir(exist_ok=True)

    # ========== Nur .mpr verwenden =========
    mpr_files = []

    for file_path in input_dir.iterdir():
        if file_path.is_file() and file_path.suffix.lower() == ".mpr":
            mpr_files.append(file_path)

    mpr_files = sorted(mpr_files)

    if len(mpr_files) == 0:
        exit("No .mpr files found in input directory")

    # =====================================================
    # Leere Listen etc.
    # =====================================================

    counters = {}  # zählt verarbeitete Zeilen pro measurement_id -> hier Methode für pandas nötig
    skipped_rows = {}  # Zählt Zeilen, die übersprungen wurden weil keine validen Daten


    # ========== Durch Dateien gehen =========
    for file_path in mpr_files:
        print(f"Importing: {file_path.name}")


        #=====================================================
        # Datei öffnen, Dataframe erzeugen
        #=====================================================

        mpr_file = BioLogic.MPRfile(str(file_path))
        df = pd.DataFrame(mpr_file.data)
        df = df.reset_index(drop=True)


        #=====================================================
        # Dataframe an Format anpassen
        #=====================================================



        df = normalize_values(df, file_path)

        # GGF. müssen wir für Impedanzdaten hier noch eine Umwandlung machen


        # =====================================================
        # Loop-Information per Time-Jump-Heuristik einfügen
        # =====================================================

        # Loop 1 number
        min_loop_time_jump_s = 5 * 60
        min_loop_segment_rows = 50

        df, loop_info = apply_time_jump_loop_detection(
            df=df,
            time_column="Time /s",
            min_loop_time_jump_s=min_loop_time_jump_s,
            min_loop_segment_rows=min_loop_segment_rows,
        )

        # Loop 2 number
        df["loop 2 number"] = ""

        # Loop 3 number
        df["loop 3 number"] = ""

        # Loop 4 number
        df["loop 4 number"] = ""

        #=====================================================
        # Dataframe Spalten für Export festlegen
        #=====================================================

        columns_to_keep = [
            "Time /s",
            "Step",
            "Task",
            "Cycle number",
            "Loop 1 number",
            "Loop 2 number",
            "Loop 3 number",
            "Loop 4 number",
            "U /V",
            "I /A",
            "Frequency /Hz",
            "Impedance module /Ohms",
            "Impedance phase /rad",
            "Real impedance /Ohms",
            "- Imaginary impedance /Ohms",
            "BTLab Ns",
        ]

        for column in columns_to_keep:
            if column not in df.columns:
                df[column] = ""

        df = df[columns_to_keep]

        #=====================================================
        # Dataframe als CSV exportieren
        #=====================================================

        first_group_for_file = True

        for group_id, group in df.groupby(["Step", "Task", "Loop 1 number"], dropna=False):
            step, task, loop1 = group_id
            segment = "main"
            group = group.copy()
            group["Segment"] = "main"
            measurement_id = (step, task, loop1, segment)

            if pd.isna(loop1) or loop1 == "":
                output_path = output_dir / f"{file_path.stem}_{step}_no_loop.csv"
            else:
                output_path = output_dir / f"{file_path.stem}_{step}_{loop1:.0f}.csv"

            # ========== Export erstmal nur für LSV und CstV =========

            valid_rows = group["U /V"].notna() & group["I /A"].notna()
            group_valid = group[valid_rows].copy()

            skipped_invalid = len(group) - len(group_valid)
            skipped_short_segment_rows = loop_info["skipped_short_segment_rows"]

            # Skipped short loop segments belong to the source file, not to one specific loop.
            # To keep compatibility with the existing skipped_rows report, they are added
            # only once to the first exported group of this source file.
            # Bei häufigerer Verwendung wäre ein eigener Report hier sinnvoll!
            if first_group_for_file:
                skipped_short = skipped_short_segment_rows
                first_group_for_file = False
            else:
                skipped_short = 0

            skipped_rows[measurement_id] = skipped_invalid + skipped_short

            counters[measurement_id] = len(group_valid)

            group_valid.to_csv(output_path, index=False)

        # ========== Später: Ergebnisse an Main zurückgeben =========

    return counters, skipped_rows