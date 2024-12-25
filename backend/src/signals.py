import numpy as np

def generate_sine_wave(frequency, amplitude, phase, duration, sample_rate=44100):
    """
    生成正弦波信号。

    :param frequency: 正弦波的频率 (Hz)
    :param amplitude: 正弦波的幅度
    :param phase: 正弦波的相位 (弧度)
    :param duration: 信号的持续时间 (秒)
    :param sample_rate: 采样率，默认为44100 Hz
    :return: 生成的信号数据
    """
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    signal = amplitude * np.sin(2 * np.pi * frequency * t + phase)
    return [float(s) for s in signal if not np.isnan(s)]  # 确保没有 NaN 值
def generate_square_wave(frequency, amplitude, duty_cycle, duration, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    signal = amplitude * np.sign(np.sin(2 * np.pi * frequency * t))
    signal = np.where(signal > 0, amplitude, -amplitude * (1 - duty_cycle))
    return [float(s) for s in signal if not np.isnan(s)]

def generate_triangle_wave(frequency, amplitude, duration, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    signal = amplitude * 2 / np.pi * np.arcsin(np.sin(2 * np.pi * frequency * t))
    return [float(s) for s in signal if not np.isnan(s)]