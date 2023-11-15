from pymongo import MongoClient
import os
from tensorflow.keras.models import load_model
from kapre.time_frequency import STFT, Magnitude, ApplyFilterbank, MagnitudeToDecibel
from clean import downsample_mono, envelope
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from matplotlib.gridspec import GridSpec
import librosa

# Verbindung zur MongoDB herstellen
client = MongoClient('mongodb://localhost:27017/')  # Ändern Sie die Verbindungsdaten entsprechend

# Datenbank und Sammlung auswählen
db = client['audio_classification']
collection = db['audio_data']

# Funktion zum Sammeln von Audiodateipfaden im Ordner (rekursiv)
def collect_audio_files(folder_path):
    audio_files = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".WAV"):
                audio_files.append(os.path.join(root, file))
    return audio_files

# Funktion zum Laden der Modelle
def load_models(model_paths):
    models = []
    for model_path in model_paths:
        model = load_model(model_path, custom_objects={
            'STFT': STFT,
            'Magnitude': Magnitude,
            'ApplyFilterbank': ApplyFilterbank,
            'MagnitudeToDecibel': MagnitudeToDecibel
        })
        models.append(model)
    return models

# Funktion zur Klassifikation und Speicherung der Ergebnisse
def classify_and_store_results(audio_files, models):
    for audio_file_path in audio_files:

        # Extrahieren von Informationen aus dem Dateinamen
        filename = os.path.basename(audio_file_path)
        parts = filename.split('_')
        location = parts[0]
        date_str, time_str = parts[1], parts[2][:6]
        date = '{}-{}-{}'.format(date_str[:4], date_str[4:6], date_str[6:])
        weekday = pd.Timestamp(date).day_name()

        rate, wav = downsample_mono(audio_file_path, 16000)
        mask, env = envelope(wav, rate, threshold=20)
        clean_wav = wav[mask]

        # Konvertierung in Gleitkommazahlen
        clean_wav = clean_wav.astype(float) / np.iinfo(clean_wav.dtype).max

        # Parameter
        dt = 3.0  # Zeit in Sekunden für die Audio-Probe
        step = int(rate)  # 3 Sekunden Schrittgröße
        window = int(rate * dt)  # 3 Sekunden Fenstergröße

        # Die Gesamtlänge des Audios in Sekunden
        total_seconds = int(clean_wav.shape[0] / rate)

        classifications = []

        for i in range(0, clean_wav.shape[0] - window + 1, step):
            sample = clean_wav[i:i+window]
            sample = sample.reshape(-1, 1)

            # RMS Energy berechnen
            rms = librosa.feature.rms(y=sample.flatten(), frame_length=window, hop_length=window)[0]
            rms_energy = str(np.mean(rms))
            start_time = pd.Timestamp(f'{date} {time_str[:2]}:{time_str[2:4]}:{time_str[4:]}')
            current_time = (start_time + pd.to_timedelta(i // rate, 's')).time().strftime('%H:%M:%S')

            class_binary = []
            confidences = []

            for model in models:
                X_batch = np.array([sample], dtype=np.float32)
                
                y_pred = model.predict(X_batch)
                y_mean = np.mean(y_pred, axis=0)
                predicted_label = int(np.argmax(y_mean))

                class_binary.append(predicted_label)
                confidences.append(float(y_mean[predicted_label]))

            classifications.append({
                'Time': current_time,
                'ClassBinary': class_binary,
                'Confidences': confidences,
                'RMS-Energy': rms_energy
            })

        document = {
            'Dateiname': filename,
            'Ort': location,
            'Datum': date,
            'Wochentag': weekday,
            'Classifications': classifications
        }    

        # Fügen Sie das Dokument zur MongoDB-Sammlung hinzu
        collection.insert_one(document)
        print(document)

# Sammeln Sie die Audiodateipfade im gewünschten Ordner (rekursiv)
audio_folder_path = "raw_audio"  # Ändern Sie den Pfad entsprechend
audio_files = collect_audio_files(audio_folder_path)

# Laden Sie die Modelle
model_paths = [
    "models/def_models/conv1d_vogel.h5",
    "models/def_models/conv1d_laerm.h5",
    "models/def_models/conv1d_natur.h5",
    "models/def_models/conv1d_stille.h5",
]
models = load_models(model_paths)

# Führen Sie die Klassifikation und das Speichern der Ergebnisse durch
classify_and_store_results(audio_files, models)

# Schließen Sie die MongoDB-Verbindung, wenn Sie fertig sind
client.close()
