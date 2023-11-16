from pymongo import MongoClient
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# MongoDB-Verbindungsinformationen
client = MongoClient("mongodb://localhost:27017/") # Passen Sie dies an Ihre MongoDB-Instanz an
db = client["ClassifiedAudioSNP"] # Datenbankname
collection = db["aggregated_files_per_day"] # Sammlungsname

# Daten für ein bestimmtes Datum abrufen
date_to_retrieve = "2023-09-12"
query = {"Date": date_to_retrieve}
document = collection.find_one(query)

# Überprüfen, ob Dokument vorhanden ist
if document:
    # Umwandeln der Stundeninformationen in einen DataFrame
    hours_info = pd.DataFrame(document["hours_info"])
    hours_info["Time"] = pd.to_datetime(hours_info["Time"]).dt.time

    # Umwandeln von verschachtelten Strukturen in der Spalte average_RMS_dB in numerische Werte
    def convert_to_numeric(value):
        if isinstance(value, dict) and "$numberDouble" in value:
            return float('nan') if value["$numberDouble"] == "NaN" else float(value["$numberDouble"])
        return value

    hours_info["average_RMS_dB"] = hours_info["average_RMS_dB"].apply(convert_to_numeric)

    # Behandeln von NaN-Werten in der Spalte average_RMS_dB
    hours_info["average_RMS_dB"].fillna(0, inplace=True)

    # Umstrukturierung des DataFrames für die Heatmap
    heatmap_data = hours_info.set_index("Time").T

    # Heatmap erstellen
    plt.figure(figsize=(15, 5))
    sns.heatmap(heatmap_data, annot=False, fmt=".1f", cmap="viridis")
    plt.title(f"Heatmap der Klassen und average_RMS_dB am {date_to_retrieve}")
    plt.xlabel('Uhrzeit')
    plt.ylabel('Klasse / average_RMS_dB')
    plt.show()

else:
    print(f"Keine Daten für das Datum {date_to_retrieve} gefunden.")
