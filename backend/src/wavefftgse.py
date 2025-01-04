import numpy as np
from scipy.fft import fft, ifft
from scipy.signal import hilbert, butter, filtfilt

class SignalProcessor:
    def __init__(self, data, sample_rate=1000):
        self.data = data.get('x', [])  # 假设数据是一个包含 'x' 和 'y' 的字典
        self.sample_rate = sample_rate
        self._validate_data()

    def _validate_data(self):
        """验证并清理数据"""
        if not isinstance(self.data, (list, np.ndarray)):
            raise ValueError("Data must be a list or numpy array")

        # 将数据转换为 numpy 数组，并确保只包含数值类型
        self.data = np.array(self.data, dtype=float)

        # 检查是否有 NaN 或者无穷大的值
        if np.isnan(self.data).any() or np.isinf(self.data).any():
            logging.warning("Data contains NaN or Inf values, which will be removed.")
            self.data = self.data[~np.isnan(self.data) & ~np.isinf(self.data)]

        if len(self.data) == 0:
            raise ValueError("No valid numeric data found in the input.")

    def get_spectrum(self):
        """计算信号的频谱"""
        yf = fft(self.data)
        xf = np.linspace(0.0, self.sample_rate/2, len(yf)//2)
        return xf, 2.0/len(yf) * np.abs(yf[:len(yf)//2])

    def integrate(self):
        """积分信号"""
        integrated_data = np.cumsum(self.data) / self.sample_rate
        return integrated_data

    def envelope_demodulation(self, high_pass_cutoff=1000):
        """执行包络解调与高通滤波"""
        analytic_signal = hilbert(self.data)
        amplitude_envelope = np.abs(analytic_signal)

        # 设计一个高通滤波器
        nyquist = 0.5 * self.sample_rate
        normal_cutoff = high_pass_cutoff / nyquist
        b, a = butter(5, normal_cutoff, btype='high', analog=False)

        # 应用滤波器到包络
        filtered_envelope = filtfilt(b, a, amplitude_envelope)
        return filtered_envelope

    def process_all(self):
        """处理所有变换并返回结果"""
        try:
            original_spectrum_x, original_spectrum_y = self.get_spectrum()
            integrated_data = self.integrate()
            integrated_spectrum_x, integrated_spectrum_y = self.get_spectrum()
            envelope_data = self.envelope_demodulation()
            envelope_spectrum_x, envelope_spectrum_y = self.get_spectrum()

            return {
                'original_data': self.data.tolist(),
                'original_spectrum': {'x': original_spectrum_x.tolist(), 'y': original_spectrum_y.tolist()},
                'integrated_data': integrated_data.tolist(),
                'integrated_spectrum': {'x': integrated_spectrum_x.tolist(), 'y': integrated_spectrum_y.tolist()},
                'envelope_data': envelope_data.tolist(),
                'envelope_spectrum': {'x': envelope_spectrum_x.tolist(), 'y': envelope_spectrum_y.tolist()}
            }
        except Exception as e:
            logging.error(f"Error processing all signals: {str(e)}")
            raise