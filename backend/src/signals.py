import numpy as np

def generate_sine_wave(frequency, amplitude, phase, duration, sample_rate):
    """
    生成正弦波信号。

    :param frequency: 正弦波的频率 (Hz)
    :param amplitude: 正弦波的幅度
    :param phase: 正弦波的相位 (弧度)
    :param duration: 信号的持续时间 (秒)
    :param sample_rate: 采样率，默认为1000 Hz
    :return: 生成的信号数据
    """
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    signal = amplitude * np.sin (2 * np.pi * frequency * t + phase)
    return signal  # 直接返回 NumPy 数组
def generate_square_wave(frequency, amplitude, duty_cycle, duration, sample_rate):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    cycle = np.mod (t * frequency, 1.0)  # 将时间映射到 [0, 1] 的周期内
    signal = np.where (cycle < duty_cycle, amplitude, -amplitude)
    return signal  # 直接返回 NumPy 数组

def generate_triangle_wave(frequency, amplitude, duration, sample_rate):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    cycle = np.mod (t * frequency, 1.0)  # 将时间映射到 [0, 1] 的周期内
    signal = 4 * amplitude * np.abs (cycle - 0.5) - amplitude
    return signal  # 直接返回 NumPy 数组