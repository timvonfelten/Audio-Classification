from pymongo import MongoClient
import json

# MongoDB-Verbindungsinformationen
client = MongoClient("mongodb://localhost:27017/") # Passen Sie dies an Ihre MongoDB-Instanz an
db = client["ClassifiedAudioSNP"] # Datenbankname
collection = db["aggregated_files_per_day"] # Sammlungsname

# Abrufen aller Dokumente aus der Sammlung
documents = collection.find({})

# Speichern jedes Dokuments als JSON-File
for idx, document in enumerate(documents):
    with open(f"document_{idx}.json", "w") as file:
        # Konvertieren des Dokuments in ein JSON-Format und Speichern
        json.dump(document, file, default=str) # default=str, um Datumsformate usw. korrekt zu handhaben

print("Alle Dokumente wurden gespeichert.")
