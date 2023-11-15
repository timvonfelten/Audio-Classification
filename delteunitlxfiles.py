import os
import random

# Pfad zum Ordner, in dem Sie Dateien löschen möchten
ordner_pfad = '/Users/timvonfelten/LocalStorage/KlassifizierteDatenSNP/Trainingsdaten/T_Natur/KeinNatur'

# Maximale Anzahl von Dateien, die im Ordner bleiben sollen
max_anzahl_dateien = 500

# Liste der Dateien im Ordner
dateien = os.listdir(ordner_pfad)

# Prüfen Sie, ob mehr Dateien als max_anzahl_dateien vorhanden sind
while len(dateien) > max_anzahl_dateien:
    # Zufällig eine Datei auswählen
    zu_loeschende_datei = random.choice(dateien)
    
    # Den vollen Pfad zur zu löschenden Datei erstellen
    datei_pfad = os.path.join(ordner_pfad, zu_loeschende_datei)
    
    try:
        # Datei löschen
        os.remove(datei_pfad)
        print(f'Datei gelöscht: {zu_loeschende_datei}')
    except Exception as e:
        print(f'Fehler beim Löschen der Datei {zu_loeschende_datei}: {str(e)}')
    
    # Liste der Dateien aktualisieren
    dateien = os.listdir(ordner_pfad)

print(f'Es sind jetzt {len(dateien)} Dateien im Ordner.')
