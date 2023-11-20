from pymongo import MongoClient
from datetime import datetime

# MongoDB Verbindung einrichten
client = MongoClient("mongodb://localhost:27017/")  # Ersetzen Sie dies durch Ihre MongoDB-Verbindungsinformationen
db = client["ClassifiedAudioSNP"]
collection = db["audio_classification_test"]



# Funktion, um den Wochentag zu ermitteln
def get_weekday(date):
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    return days[date.weekday()]

# Durchsuchen Sie jedes Dokument
for document in collection.find():
    filename = document['Filename']
    
    # Extrahieren Sie die Informationen aus dem Filename
    parts = filename.split('_')
    place = parts[0]
    date_str = parts[1]
    time_str = parts[2].split('.')[0]
    
    # Konvertieren Sie das Datum und die Uhrzeit in ein datetime-Objekt
    datetime_obj = datetime.strptime(date_str + time_str, '%Y%m%d%H%M%S')
    
    # Extrahieren Sie Datum, Uhrzeit und Wochentag
    date = datetime_obj.strftime('%Y-%m-%d')
    time = datetime_obj.strftime('%H:%M:%S')
    weekday = get_weekday(datetime_obj)
    
    # Aktualisieren Sie das Dokument
    collection.update_one({'_id': document['_id']}, {'$set': {'Place': place, 'Date': date, 'Time': time, 'Weekday': weekday}})

client.close()
