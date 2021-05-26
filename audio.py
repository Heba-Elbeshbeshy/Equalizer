import numpy as np
import matplotlib.pyplot as plt
import wave
import struct
from math import pi
import soundfile

num_samples = 4800
amplitude = 800
sampling_rate = 4800.0
# Freq=[100,150,400,500,700,1000,1200,1500]
Freq=[100, 200 , 300 , 400 , 500 ]
file = "test3.wav"

t= np.arange(0,1,1/sampling_rate)

sine_wave = 0

#sine_wave = np.sin(2*pi*100*t)

for i in Freq:
    sine_wave += np.sin(2*pi*i*t)

nframes=num_samples
comptype="NONE"
compname="not compressed"
nchannels=1
sampwidth=2    
wav_file=wave.open(file, 'w')

wav_file.setparams((nchannels, sampwidth, int(sampling_rate), nframes, comptype, compname))
for s in sine_wave:
    wav_file.writeframes(struct.pack('h', int(s*amplitude)))