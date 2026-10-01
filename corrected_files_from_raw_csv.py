
from pathlib import Path
import pandas as pd


def corrected_files(input_folder: Path, output_folder: Path):

    # Input und Output Directory

    input_dir = Path(input_folder)
    if not input_dir.is_dir():
        exit("Input directory does not exist")

    output_dir = Path(output_folder)
    output_dir.mkdir(exist_ok=True)

    # Übergabe Dict Dokumentation

    corrected_counter = {}

    # File öffnen, Output Path

    for file_path in input_dir.glob("*.csv"):
        output_path = output_dir / (file_path.stem + "_corrected.csv")

        df = pd.read_csv(file_path)

        # Measurement-ID für Dokumentation
        if df.empty:
            continue
        measurement_id = (df["Step"].iloc[0], df["Task"].iloc[0], df["Loop 1 number"].iloc[0], df["Segment"].iloc[0])

        # Pandas Series erzeugen -> hier direkt im Dataframe, da wir den in die CSV schreiben

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
        ]

        for column in numeric_columns:
            if column in df.columns:
                df[column] = pd.to_numeric(df[column], errors="coerce")

        # Schreiben
        df.to_csv(output_path, index=False)

        # Geschriebene Zeilen dokumentieren
        counter = len(df)
        corrected_counter[measurement_id] = counter


    return corrected_counter