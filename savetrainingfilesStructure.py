import os
import csv

def list_files_recursive(path, csv_file):
    with open(csv_file, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['File Path', 'File Name', 'File Size (Bytes)'])
        
        for root, dirs, files in os.walk(path):
            for name in files:
                file_path = os.path.join(root, name)
                file_size = os.path.getsize(file_path)
                writer.writerow([file_path, name, file_size])

# Verzeichnis, das durchsucht werden soll
directory_to_scan = '/Users/timvonfelten/LocalStorage/KlassifizierteDatenSNP/all_cleaned'

# Name der CSV-Datei, in der die Ergebnisse gespeichert werden sollen
output_csv = 'logs/files_list_20112023.csv'

list_files_recursive(directory_to_scan, output_csv)
