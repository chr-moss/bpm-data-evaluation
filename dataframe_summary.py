from pathlib import Path
import pandas as pd

def dataframe_summary(input_path: Path, output_path: Path):

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

        # Liste von Dataframes erstellen
        dataframes.append(df)

    # 3. alle DataFrames mit pd.concat zusammenführen
    # Liste mit concat zusammenführen zu neuem großen Dataframe
    all_data = pd.concat(dataframes)

    # 4. groupby(["Step", "Task"]) Summary erzeugen
    all_data.groupby(["Step", "Task", "Loop 1 number", "Segment"])

    summary = all_data.groupby(["Step", "Task", "Loop 1 number", "Segment"]).agg(
        Rows=("Time /s", "count"),
        Start_time=("Time /s", "first"),
        End_time=("Time /s", "last"),
        First_U=("U /V", "first"),
        Last_U=("U /V", "last"),
        First_I=("I /A", "first"),
        Last_I=("I /A", "last"),
    ).reset_index()

    summary["Duration /s"] = summary["End_time"] - summary["Start_time"]
    summary["Duration /min"] = summary["Duration /s"]/60
    summary["Duration /h"] = summary["Duration /s"]/3600

    # 5. Summary als CSV speichern

    summary.to_csv(output_dir / "dataframe_summary.csv", index=False)

    print()
    print("=================================================================================")
    print("Dataframe summary:")
    print("=================================================================================")
    print(summary)