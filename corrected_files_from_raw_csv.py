
from pathlib import Path
import pandas as pd


def corrected_files(input_folder: Path, output_folder: Path):

    # =================   File Handling   ======================

    # Input und Output Directory

    input_dir = Path(input_folder)
    if not input_dir.is_dir():
        exit("Input directory does not exist")

    output_dir = Path(output_folder)
    output_dir.mkdir(exist_ok=True)

    # Übergabe Dict Dokumentation - Container erstellen

    corrected_counter = {}

    # File öffnen, Output Path

    for file_path in input_dir.glob("*.csv"):
        output_path = output_dir / (file_path.stem + "_corrected.csv")

        df = pd.read_csv(file_path)

        # =================   Measurement ID erzeugen   ======================

        if df.empty:
            continue

        step = df["Step"].iloc[0]
        task = df["Task"].iloc[0]
        loop1 = df["Loop 1 number"].iloc[0]
        segment = df["Segment"].iloc[0]

        loop_id = None if pd.isna(loop1) else loop1

        measurement_id = (step, task, loop_id, segment)

        # =================   Ausgewählte Numeric Columns erstellen   ======================

        numeric_columns = [
            "Time /s",
            "Cycle number",
            "U /V",
            "I /A",
            "Frequency /Hz",
            "Impedance module /Ohms",
            "Impedance phase /rad",
            "Real impedance /Ohms",
            "- Imaginary impedance /Ohms",
            "AC amplitude /V",
        ]

        for column in numeric_columns:
            if column in df.columns:
                df[column] = pd.to_numeric(df[column], errors="coerce")

        # =================   Schreiben und Dokumentieren   ======================

        # Schreiben
        df.to_csv(output_path, index=False)

        # Geschriebene Zeilen dokumentieren
        counter = len(df)
        corrected_counter[measurement_id] = counter


    return corrected_counter