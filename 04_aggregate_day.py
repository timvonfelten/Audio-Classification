from pymongo import MongoClient

# MongoDB Verbindung einrichten
client = MongoClient("mongodb://localhost:27017/")
db = client["ClassifiedAudioSNP"]
collection = db["aggregated_files"]  # Verwenden Sie die 'aggregated_files' Kollektion

pipeline = [
    {
        "$group": {
            "_id": {"Date": "$Date", "Place": "$Place"},
            "hours_info": {
                "$push": {
                    "Time": "$Time",
                    "stille_count": "$stille_count",
                    "vogel_count": "$vogel_count",
                    "laerm_count": "$laerm_count",
                    "natur_count": "$natur_count",
                    "average_RMS_dB": "$average_RMS_dB"  # Verwenden Sie den Durchschnittswert von RMS_dB
                }
            }
        }
    },
    {
        "$addFields": {
            "hours_info": {
                "$sortArray": {
                    "input": "$hours_info",
                    "sortBy": {"Time": 1}
                }
            }
        }
    },
    {
        "$project": {
            "_id": 0,
            "Date": "$_id.Date",
            "Place": "$_id.Place",
            "hours_info": "$hours_info"
        }
    },
    {
        "$out": "aggregated_files_per_day"  # Speichern Sie das Ergebnis in einer neuen Kollektion
    }
]

# Führen Sie die Aggregationspipeline aus
collection.aggregate(pipeline)
