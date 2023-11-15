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

model = load_model("models/conv1d.h5", custom_objects={
    'STFT': STFT,
    'Magnitude': Magnitude,
    'ApplyFilterbank': ApplyFilterbank,
    'MagnitudeToDecibel': MagnitudeToDecibel
})

# Modellarchitektur anzeigen
model.summary()

# Gewichte für jede Schicht anzeigen
for layer in model.layers:
    weights = layer.get_weights()
    print(f"Gewichte der Schicht {layer.name}: {weights}")

# Alternativ können Sie die Gewichte als Array ausgeben
weights = model.get_weights()
print(weights)
