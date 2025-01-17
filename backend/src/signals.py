import numpy as np

def generate_sine_wave(frequency, amplitude, phase, duration, sample_rate):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    signal = amplitude * np.sin(2 * np.pi * frequency * t + phase)
    return signal

def generate_square_wave(frequency, amplitude, duty_cycle, duration, sample_rate):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    cycle = np.mod(t * frequency, 1.0)
    signal = np.where(cycle < duty_cycle, amplitude, -amplitude)
    return signal

def generate_triangle_wave(frequency, amplitude, duration, sample_rate):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    cycle = np.mod(t * frequency, 1.0)
    signal = 4 * amplitude * np.abs(cycle - 0.5) - amplitude
    return signal