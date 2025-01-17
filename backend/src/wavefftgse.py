import logging
import numpy as np
from numpy.fft import fft
from scipy.signal import hilbert, butter, filtfilt


class SignalProcessor:
    def __init__(self, data, sample_rate, high_pass_cutoff=None):
        self.sample_rate = sample_rate
        self.nyquist_freq = 0.5 * sample_rate
        self.high_pass_cutoff = high_pass_cutoff

        if isinstance(data, dict):  # 处理 JSON 格式的数据
            self.x_data = np.array(data.get('x', []))
            self.y_data = np.array(data.get('y', []))
        elif isinstance(data, str):  # 处理文本格式的数据
            lines = data.strip().splitlines()
            if len(lines) == 1:  # 单行数据
                self.y_data = np.array([float(x) for x in lines[0].split(',')])
                self.x_data = np.arange(len(self.y_data)) / self.sample_rate
            else:  # X-Y两列数据
                data = np.loadtxt(StringIO('\n'.join(lines)), delimiter=',', unpack=True)
                self.x_data = data[0]
                self.y_data = data[1]
        elif isinstance(data, (list, np.ndarray)):  # 处理列表或 NumPy 数组格式的数据
            data = np.array(data)
            if len(data.shape) == 1:  # 单行数据
                self.y_data = data
                self.x_data = np.arange(len(self.y_data)) / self.sample_rate
            else:  # X-Y两列数据
                self.x_data = data[0]
                self.y_data = data[1]
        else:
            raise ValueError("Unsupported data format")

        self._validate_data()
        logging.info("Data validation completed.")

    def _validate_data(self):
        """验证并清理数据"""
        for attr in ['x_data', 'y_data']:
            data = getattr(self, attr)
            if not isinstance(data, (np.ndarray)):
                raise ValueError(f"{attr} must be a numpy array")

            # 检查是否有 NaN 或者无穷大的值
            if np.isnan(data).any() or np.isinf(data).any():
                logging.warning(f"{attr} contains NaN or Inf values, which will be removed.")
                setattr(self, attr, data[~np.isnan(data) & ~np.isinf(data)])

            if len(data) == 0:
                raise ValueError(f"No valid numeric data found in the {attr}.")

        # 确保 x 和 y 数据长度一致
        if len(self.x_data) != len(self.y_data):
            raise ValueError("x and y data must have the same length")

    def get_spectrum(self):
        """计算信号的频谱"""
        yf = fft(self.y_data)
        n = len(yf)
        xf = np.linspace(0.0, self.sample_rate / 2, n // 2 + 1)
        return xf, 2.0 / n * np.abs(yf[:n // 2 + 1])

    def integrate(self):
        """积分信号，并返回积分波形和频谱数据"""
        integrated_data = np.cumsum(self.y_data) / self.sample_rate
        freqs, spectrum = self.get_spectrum_from_data(integrated_data)
        return self.x_data, integrated_data, freqs, spectrum

    def get_envelope(self, high_pass_cutoff):
        """获取包络波形及其频谱"""
        analytic_signal = hilbert(self.y_data)
        envelope = np.abs(analytic_signal)

        if high_pass_cutoff is not None and high_pass_cutoff > 0:
            nyquist = 0.5 * self.sample_rate
            normal_cutoff = high_pass_cutoff / nyquist
            b, a = butter(5, normal_cutoff, btype='high', analog=False)
            envelope = filtfilt(b, a, envelope)

        freqs, spectrum = self.get_spectrum_from_data(envelope)
        return self.x_data, envelope, freqs, spectrum

    def get_spectrum_from_data(self, data):
        """从给定的数据中计算频谱"""
        yf = fft(data)
        n = len(yf)
        xf = np.linspace(0.0, self.sample_rate / 2, n // 2 + 1)
        return xf, 2.0 / n * np.abs(yf[:n // 2 + 1])

    def process_all(self, high_pass_cutoff):
        """处理所有变换并返回结果"""
        try:
            original_spectrum_x, original_spectrum_y = self.get_spectrum()
            logging.info("Original spectrum computed.")

            integrated_data_x, integrated_data_y, integrated_spectrum_x, integrated_spectrum_y = self.integrate()
            logging.info("Integrated spectrum computed.")

            envelope_data_x, envelope_data_y, envelope_spectrum_x, envelope_spectrum_y = self.get_envelope(
                high_pass_cutoff=high_pass_cutoff)
            logging.info("Envelop spectrum computed.")

            # 使用 numpy 的 tolist() 方法只针对 NumPy 数组
            return {
                'original_data': {'x': self.x_data.tolist(), 'y': self.y_data.tolist()},
                'original_spectrum': {'x': original_spectrum_x.tolist(), 'y': original_spectrum_y.tolist()},
                'integrated_data': {'x': integrated_data_x.tolist(), 'y': integrated_data_y.tolist()},
                'integrated_spectrum': {'x': integrated_spectrum_x.tolist(), 'y': integrated_spectrum_y.tolist()},
                'envelope_data': {'x': envelope_data_x.tolist(), 'y': envelope_data_y.tolist()},
                'envelope_spectrum': {'x': envelope_spectrum_x.tolist(), 'y': envelope_spectrum_y.tolist()}
            }
        except Exception as e:
            logging.error(f"Error processing all signals: {str(e)}")
            raise ValueError(f"Failed to process signals: {str(e)}") from e



