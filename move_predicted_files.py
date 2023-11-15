import csv
import os
import shutil

def move_audio_files(audio_folder, csv_file, output_folder):
    with open(csv_file, 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        header = next(csvreader)  # Überspringe den Header der CSV-Datei

        for row in csvreader:
            filename, actual_class, predicted_class, confidence = row

            src = os.path.join(audio_folder, filename)
            dest_folder = os.path.join(output_folder, predicted_class)
            dest = os.path.join(dest_folder, filename)

            if not os.path.exists(dest_folder):
                os.makedirs(dest_folder)

            if os.path.exists(src):
                shutil.move(src, dest)
            else:
                print(f"Datei {filename} nicht gefunden.")

if __name__ == "__main__":
    audio_folder = "/Users/timvonfelten/Library/Mobile Documents/com~apple~CloudDocs/04_Studium/500/Geoinformatik/Analyse_Tutorial/audioclassifier/input"
    csv_file = "/Users/timvonfelten/LocalStorage/Audio-Classification_seth/logs/stats.csv"
    output_folder = "/Users/timvonfelten/LocalStorage/KlassifizierteDatenSNP/output_ki_test"

    move_audio_files(audio_folder, csv_file, output_folder)
