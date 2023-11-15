from tensorflow.keras.models import load_model
from kapre.time_frequency import STFT, Magnitude, ApplyFilterbank, MagnitudeToDecibel
from clean import downsample_mono, envelope
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import pandas as pd
from matplotlib.gridspec import GridSpec
import librosa

# Lade das trainierte .h5 Modell
model = load_model("/Users/timvonfelten/LocalStorage/Audio-Classification_seth/models/def_models/conv1d_stille.h5", custom_objects={
    'STFT': STFT,
    'Magnitude': Magnitude,
    'ApplyFilterbank': ApplyFilterbank,
    'MagnitudeToDecibel': MagnitudeToDecibel
})

# Lade das .wav File
audio_file_path = "/Users/timvonfelten/LocalStorage/Audio-Classification_seth/raw_audio/ls08_20230512_064500.WAV"
rate, wav = downsample_mono(audio_file_path, 16000)
mask, env = envelope(wav, rate, threshold=20)
clean_wav = wav[mask]

# Parameter
dt = 3.0  # Zeit in Sekunden für die Audio-Probe
step = int(rate)  # 1 Sekunde Schrittgröße
window = int(rate * dt)  # 3 Sekunden Fenstergröße

# Initialisiere leere Liste für Klassifikationsergebnisse und Statistiken
classification_results = []
stats = []

def calculate_rms_db(audio_segment):
    # Berechnung des quadratischen Mittelwerts (Root Mean Square, RMS)
    rms_value = np.sqrt(np.mean(np.square(audio_segment)))
    # Umrechnung des RMS-Werts in Dezibel
    rms_db = 20 * np.log10(rms_value)
    return rms_db

# Aufteilen des Audios und Klassifizierung
for i in range(0, clean_wav.shape[0] - window + 1, step):
    sample = clean_wav[i:i+window]
    sample = sample.reshape(-1, 1)
    X_batch = np.array([sample], dtype=np.float32)
    
    y_pred = model.predict(X_batch)
    y_mean = np.mean(y_pred, axis=0)
    predicted_label = np.argmax(y_mean)
    
    # Berechnung des RMS dB Werts für jede Sekunde im aktuellen Fenster
    rms_db_values = [calculate_rms_db(sample[j:j+rate]) for j in range(0, len(sample), rate)]
    
    classification_results.append(predicted_label)
    stats.append({
        'Filename': os.path.basename(audio_file_path),
        'Seconds': i / rate,
        'From_To': f"{i/rate}-{(i+window)/rate}",
        'Predicted Class': predicted_label,
        'Confidence': y_mean[predicted_label],
        'RMS dB': rms_db_values  # Dies wird eine Liste von RMS dB Werten für jede Sekunde im aktuellen Fenster zurückgeben
    })
    print(({
        'Filename': os.path.basename(audio_file_path),
        'Seconds': i / rate,
        'From_To': f"{i/rate}-{(i+window)/rate}",
        'Predicted Class': predicted_label,
        'Confidence': y_mean[predicted_label],
        'RMS dB': rms_db_values
    }))
print(len(classification_results))


rolling_means = []
for i in range(0, len(classification_results) - 2):
    mean_value = np.mean(classification_results[i:i + 3])
    rolling_means.append(mean_value)

# Anzahl der Spalten und Zeilen für die Heatmap
num_columns = len(rolling_means) // 2
num_rows = 2

# Erstellen Sie die Heatmap
fig, axs = plt.subplots(num_rows, 1, figsize=(12, 6))
for i in range(num_rows):
    sns.heatmap([rolling_means[i*num_columns:(i+1)*num_columns]], 
                ax=axs[i],
                annot=True, cmap='RdYlGn', 
                xticklabels=range(i*num_columns, (i+1)*num_columns),
                square=True, cbar=False)  # Keine automatische Farblegende

    axs[i].set_xlabel('Zeit in Sekunden')
    axs[i].set_yticks([], [])

# Titel hinzufügen
plt.suptitle(f'Klassifikation für {os.path.basename(audio_file_path)}', fontsize=20)

# Einstellen des Abstands zwischen Plot und Legende
plt.subplots_adjust(bottom=0.1)

# Erstellen Sie die Legende
cbar_ax = fig.add_axes([0.35, 0.1, 0.3, 0.02])  # Position und Größe der Legende
cbar = plt.colorbar(axs[-1].collections[0], cax=cbar_ax, orientation='horizontal')
cbar.set_ticks([0, 1])
cbar.set_ticklabels(['Kein Vogel', 'Vogel'])

plt.show()

def calculate_rolling_means(classification_results):
    rolling_means = []
    for i in range(0, len(classification_results) - 2):
        mean_value = np.mean(classification_results[i:i + 3])
        rolling_means.append(mean_value)
    return rolling_means


# Gleitende Mittelwerte berechnen
rolling_means = calculate_rolling_means(classification_results)

# Ihr vorhandener Code
num_seconds = len(stats)  # Jeder Eintrag in 'stats' repräsentiert eine Sekunde

# Berechnung des gemittelten Lärmwerts für jede Sekunde
avg_rms_db = [np.nanmean(stats[i]['RMS dB']) for i in range(num_seconds)]

# Ersetzen von nan Durchschnittswerten durch 0
avg_rms_db = [0 if np.isnan(value) else value for value in avg_rms_db]

# Farben für die Balken basierend auf den gleitenden Mittelwerten
colors = [(1 - value, value, 0.2) for value in rolling_means]

# Erstellen des Säulendiagramms
fig, ax = plt.subplots(figsize=(12, 6))

# Position der Balken
positions = np.arange(num_seconds)

# Zeichnen der Balken
bars = plt.bar(positions, avg_rms_db, color=colors)  # Farben basierend auf den gleitenden Mittelwerten

# Achsenbeschriftung und Titel
ax.set_xlabel('Zeit in Sekunden')
ax.set_ylabel('Durchschnittlicher Lärmwert (dB)')
plt.xticks(positions, [f'{i}-{i+1}' for i in positions], rotation=90)  # X-Achsen-Beschriftung als Zeitbereich, mit 45-Grad-Drehung
plt.title(f'Klassifikation und Lärmwert für {os.path.basename(audio_file_path)}')

# Legende
from matplotlib.lines import Line2D
legend_elements = [Line2D([0], [0], color='g', lw=4, label='Vogel'),
                   Line2D([0], [0], color='r', lw=4, label='Kein Vogel')]
ax.legend(handles=legend_elements, loc='upper right')

plt.show()
