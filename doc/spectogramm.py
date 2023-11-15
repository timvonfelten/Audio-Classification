import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy.signal import spectrogram
import numpy as np

def create_spectrogram(wav_file):
    # Lesen der WAV-Datei
    sample_rate, data = wavfile.read(wav_file)

    # Berechnung des Spektrogramms
    f, t, Sxx = spectrogram(data, sample_rate)

    # Darstellung des Spektrogramms
    plt.pcolormesh(t, f, 10 * np.log10(Sxx))
    plt.ylabel('Frequenz [Hz]')
    plt.xlabel('Zeit [s]')
    plt.title('Spektrogramm Lärm')
    plt.colorbar(label='Intensität [dB]')
    plt.show()

# Ersetzen Sie 'path_to_your_file.wav' mit dem Pfad zu Ihrer WAV-Datei
create_spectrogram('/Users/timvonfelten/LocalStorage/Audio-Classification_seth/clean_laerm/1/ls02_20230607_070000_s_54_0.wav')
