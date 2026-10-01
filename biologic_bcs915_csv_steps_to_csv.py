
from pathlib import Path
import pandas as pd

def steps_to_csv(input_folder: Path, output_folder: Path):

    # Input und Output Directory

    input_dir = Path(input_folder)
    if not input_dir.is_dir():
        exit("Input directory does not exist")

    output_dir = Path(output_folder)
    output_dir.mkdir(exist_ok=True)

    # Hilfsvariablen/Container für Output File Generation

    counters = {}  # zählt verarbeitete Zeilen pro measurement_id -> hier Methode für pandas nötig
    skipped_rows = {} # Zählt Zeilen, die übersprungen wurden weil keine validen Daten

    # File öffnen, Header Position für Pandas finden

    for file_path in input_dir.glob("*.csv"):
        header_row = None

        with open(file_path, newline="") as file:
            for line_number, line in enumerate(file):
                if line.startswith("Time /s"): # Header Row finden
                    header_row = line_number
                    break

        df = pd.read_csv(file_path, skiprows=header_row)

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
        ]
        df = df[columns_to_keep]

        for group_id, group in df.groupby(["Step", "Task", "Loop 1 number"],dropna=False):#ohne False wird REST abgeschnitten
            step, task, loop1 = group_id
            segment = "main"
            group = group.copy()
            group["Segment"] = "main"
            measurement_id = (step, task, loop1, segment)
            # NOW: Group by Loop 1 number to separate repeated method sequences.
            # Nested loops (Loop 2-4) are retained as columns but not used for grouping yet.
            if pd.isna(loop1) or loop1 == "":
                output_path = output_dir / f"{file_path.stem}_{step}_no_loop.csv"
            else:
                output_path = output_dir / f"{file_path.stem}_{step}_{loop1:.0f}.csv"
            if task == "REST": # Rest wird nicht ausgewertet daher übersprungen
                skipped_rows[measurement_id] = "n/a"
                group.to_csv(output_path, index=False)
                counters[measurement_id] = len(group)
            elif task in ["PEIS", "GEIS"]:
                hold_rows = (
                        group["U /V"].notna()
                        & group["I /A"].notna()
                        & group["Frequency /Hz"].isna()
                        & group["Impedance module /Ohms"].isna()
                        & group["Impedance phase /rad"].isna()
                        & group["Real impedance /Ohms"].isna()
                        & group["- Imaginary impedance /Ohms"].isna()
                )
                hold_valid = group[hold_rows].copy()  # reduzierter Dataframe - enthält nur TRUE & TRUE

                eis_rows = (
                        group["U /V"].notna()
                        & group["I /A"].notna()
                        & group["Frequency /Hz"].notna()
                        & group["Impedance module /Ohms"].notna()
                        & group["Impedance phase /rad"].notna()
                        & group["Real impedance /Ohms"].notna()
                        & group["- Imaginary impedance /Ohms"].notna()
                )
                eis_valid = group[eis_rows].copy()  # reduzierter Dataframe - enthält nur TRUE & TRUE

                segment = "hold"
                hold_valid["Segment"] = "hold"
                measurement_id_hold = (step, task, loop1, segment)
                hold_path = output_path.with_stem(output_path.stem + "_hold")
                hold_valid.to_csv(hold_path, index=False)

                segment = "eis"
                eis_valid["Segment"] = "eis"
                measurement_id_eis = (step, task, loop1, segment)
                eis_path = output_path.with_stem(output_path.stem + "_eis")
                eis_valid.to_csv(eis_path, index=False)

                counters[measurement_id_hold] = len(hold_valid)
                counters[measurement_id_eis] = len(eis_valid)

                skipped_rows[measurement_id_hold] = len(group) - len(hold_valid)
                skipped_rows[measurement_id_eis] = len(group) - len(eis_valid)

            else: # Für CV, VS .... alle Methoden, die nur auf Strom/Spannung basieren
                valid_rows = group["U /V"].notna() & group["I /A"].notna() # Boolean Series - liefert True/False
                group_valid = group[valid_rows].copy() # reduzierter Dataframe - enthält nur TRUE & TRUE
                counters[measurement_id] = len(group_valid)
                skipped_rows[measurement_id] = len(group) - len(group_valid)
                group_valid.to_csv(output_path, index=False)

    return counters, skipped_rows
