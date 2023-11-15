import matplotlib.pyplot as plt
import numpy as np
from pymongo import MongoClient

# Verbindung zur MongoDB herstellen
client = MongoClient('mongodb://localhost:27017/')
db = client['audio_classification']
collection = db['audio_data']

# Daten extrahieren
documents = list(collection.find({}, {'_id': 0, 'Classifications': 1, 'Dateiname': 1}))

# Für jedes Dokument in Ihren Dokumenten
for doc in documents:
    classifications = doc['Classifications']
    time_stamps = [c['Time'] for c in classifications]
    class_binary = np.array([c['ClassBinary'] for c in classifications]).T
    confidences = np.array([c['Confidences'] for c in classifications]).T
    rms_energy = np.array([float(c['RMS-Energy']) for c in classifications])

    # Farbkodierung für die kombinierte Heatmap berechnen
    colors = np.zeros((class_binary.shape[0], class_binary.shape[1], 3))
    for i in range(class_binary.shape[0]):
        for j in range(class_binary.shape[1]):
            if class_binary[i, j] == 1:
                colors[i, j] = [confidences[i, j], 0, 0]  # Rot mit Sättigung entsprechend der Confidence
            else:
                colors[i, j] = [0, confidences[i, j], 0]  # Grün mit Sättigung entsprechend der Confidence

    fig, ax1 = plt.subplots(figsize=(10, 6))

    # Kombinierte Heatmap für Klassifikation und Confidence
    ax1.imshow(colors, interpolation='nearest', aspect='auto')
    ax1.set_title(f'Kombinierte Klassifikations- und Confidence-Heatmap für {doc["Dateiname"]}')
    ax1.set_xlabel('Zeit')
    ax1.set_ylabel('Kategorie')
    ax1.set_yticks(range(class_binary.shape[0]))
    ax1.set_yticklabels(['Vogel', 'Lärm', 'Natur', 'Stille'])
    ax1.set_xticks(range(class_binary.shape[1]))
    ax1.set_xticklabels(time_stamps, rotation=90)

    # Zweite Y-Achse für das Liniendiagramm der RMS Energie
    ax2 = ax1.twinx()
    ax2.plot(rms_energy, label='RMS Energie', color='blue')
    ax2.set_ylabel('RMS Energie')
    ax2.legend(loc='upper right')

    plt.tight_layout()
    plt.show()
