from tensorflow.keras.models import load_model
from kapre.time_frequency import STFT, Magnitude, ApplyFilterbank, MagnitudeToDecibel
from clean import downsample_mono, envelope
import numpy as np
import os
from pymongo import MongoClient

# MongoDB Verbindung einrichten
client = MongoClient("mongodb://localhost:27017/")
db = client["ClassifiedAudioSNP"]
collection = db["audio_classification"]

def calculate_average_rms_db(audio_segment):
    # Berechnung des Durchschnitts des quadratischen Mittelwerts (Root Mean Square, RMS) für das gesamte Fenster
    rms_value = np.sqrt(np.mean(np.square(audio_segment)))
    # Umrechnung des RMS-Werts in Dezibel
    rms_db = 20 * np.log10(rms_value)
    return rms_db

def convert_numpy_to_python(data):
    if isinstance(data, np.generic):
        return np.asscalar(data)
    elif isinstance(data, dict):
        return {k: convert_numpy_to_python(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_numpy_to_python(v) for v in data]
    else:
        return data

# Modelle laden
model_paths = {
    'stille': "models/def_models/conv1d_stille.h5",
    'vogel': "models/def_models/conv1d_vogel.h5",
    'laerm': "models/def_models/conv1d_laerm.h5",
    'natur': "models/def_models/conv1d_natur.h5"
}

models = {name: load_model(path, custom_objects={
    'STFT': STFT,
    'Magnitude': Magnitude,
    'ApplyFilterbank': ApplyFilterbank,
    'MagnitudeToDecibel': MagnitudeToDecibel
}) for name, path in model_paths.items()}

# Verzeichnis der .wav Dateien
directory_path = "/Users/timvonfelten/LocalStorage/Audio-Classification_seth/raw_audio/"

# Gehe durch jedes File im Verzeichnis
for filename in os.listdir(directory_path):
    if filename.endswith(".WAV") or filename.endswith(".wav"):
        audio_file_path = os.path.join(directory_path, filename)
        
        # Audioverarbeitung wie zuvor
        rate, wav = downsample_mono(audio_file_path, 16000)
        mask, env = envelope(wav, rate, threshold=20)
        clean_wav = wav[mask]

        # Parameter
        dt = 1.0  # Zeit in Sekunden für die Audio-Probe
        step = int(rate * dt)  # 1 Sekunde Schrittgröße
        window = step  # 3 Sekunden Fenstergröße

        # Initialisiere leere Liste für Klassifikationsergebnisse und Statistiken
        classification_results = []

        stats = []



        # Aufteilen des Audios und Klassifizierung
        for i in range(0, clean_wav.shape[0] - window + 1, step):
            sample = clean_wav[i:i+window]
            sample = sample.reshape(-1, 1)
            X_batch = np.array([sample], dtype=np.float32)
            
            results = {}
            for model_name, model in models.items():
                y_pred = model.predict(X_batch)
                y_mean = np.mean(y_pred, axis=0)
                predicted_label = np.argmax(y_mean)
                results[model_name] = {
                    'Predicted Class': predicted_label,
                    'Confidence': y_mean[predicted_label]
                }
            
            average_rms_db = calculate_average_rms_db(sample)

            classification_result = {
                'Filename': os.path.basename(audio_file_path),
                'Seconds': i / rate,
                'From_To': f"{i/rate}-{(i+window)/rate}",
                'Average RMS dB': average_rms_db,
                'Models': results
            }
            
            classification_results.append(classification_result)
            #print(classification_result)




        # Sammeln der Klassifikationsergebnisse für jedes File
        audio_classification_results = {}

        for result in classification_results:
            filename = result['Filename']
            if filename not in audio_classification_results:
                audio_classification_results[filename] = {
                    'Filename': filename,
                    'Results': []
                }
            
            # Entfernen des 'Filename' Schlüssels aus dem Ergebnis, bevor es zur Liste hinzugefügt wird
            result_without_filename = {key: value for key, value in result.items() if key != 'Filename'}
            audio_classification_results[filename]['Results'].append(result_without_filename)

        # Konvertieren der Numpy-Datentypen und Schreiben der Daten in MongoDB
        for filename, data in audio_classification_results.items():
            data['Results'] = convert_numpy_to_python(data['Results'])
            collection.insert_one(data)

        print("Klassifikationsergebnisse wurden erfolgreich in die MongoDB geschrieben.")
