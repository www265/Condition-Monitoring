from flask import Flask, request, jsonify, send_from_directory, render_template,url_for
from werkzeug.utils import secure_filename
from flask_cors import CORS
import os
import pandas as pd
import logging
import numpy as np
from datetime import datetime
import openpyxl  # 用于读取 .xlsx 文件
import xlrd  # 用于读取 .xls 文件
from signals import generate_sine_wave, generate_square_wave, generate_triangle_wave
from wavefftgse import SignalProcessor  # 导入 SignalProcessor 类
import matplotlib.pyplot as plt
import io
import base64

# app = Flask(__name__, static_folder='uploads', static_url_path='/uploads')
app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {"origins": "http://localhost:8080"},
    r"/uploads/*": {"origins": "http://localhost:8080"}
})

# 配置上传目录和允许的文件扩展名
UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = {'csv', 'txt', 'xls', 'xlsx', 'dat'}
MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 限制文件大小为10MB

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# 设置日志配置
logging.basicConfig(filename='app.log', level=logging.INFO)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        logging.error('No file part')
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']

    if file.filename == '':
        logging.error('No selected file')
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        try:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # 根据文件扩展名选择解析方法
            file_extension = filename.lower().rsplit('.', 1)[1]
            data_info = None

            if file_extension in ('csv', 'txt'):
                try:
                    df = pd.read_csv(file_path)
                    data_info = {'shape': df.shape}
                except Exception as e:
                    logging.error(f"Error parsing CSV/TXT file {filename}: {str(e)}")
                    return jsonify({'error': f'Failed to parse CSV/TXT file: {str(e)}'}), 500
            elif file_extension == 'xlsx':
                try:
                    wb = openpyxl.load_workbook(file_path)
                    sheet_names = wb.sheetnames
                    data_info = {'sheet_names': sheet_names}
                except Exception as e:
                    logging.error(f"Error parsing XLSX file {filename}: {str(e)}")
                    return jsonify({'error': f'Failed to parse XLSX file: {str(e)}'}), 500
            elif file_extension == 'xls':
                try:
                    wb = xlrd.open_workbook(file_path)
                    sheet_names = wb.sheet_names()
                    data_info = {'sheet_names': sheet_names}
                except Exception as e:
                    logging.error(f"Error parsing XLS file {filename}: {str(e)}")
                    return jsonify({'error': f'Failed to parse XLS file: {str(e)}'}), 500
            elif file_extension == 'dat':
                # 对于 .dat 文件，我们假设它是二进制数据，不进行直接解析
                data_info = {'message': 'Binary file uploaded'}

            logging.info(f"File {filename} uploaded successfully at {datetime.now()}")
            response_data = {
                'message': 'File uploaded successfully',
                'filename': filename,
                'file_path': f"/uploads/{filename}",  # 或者你需要的实际路径
                **(data_info or {})
            }
            return jsonify(response_data), 200
        except Exception as e:
            logging.error(f"Error processing file: {str(e)}")
            return jsonify({'error': str(e)}), 500
    else:
        logging.error('File type not allowed')
        return jsonify({'error': 'File type not allowed'}), 400


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/api/generate-signal', methods=['POST'])
def generate_signal():
    try:
        # 直接从请求体中获取参数
        data = request.json

        # 验证并获取参数
        signal_type = data.get('type', 'sine').lower()
        frequency = float(data.get('frequency', 1.0))
        amplitude = float(data.get('amplitude', 1.0))
        phase = float(data.get('phase', 0.0))
        duration = float(data.get('duration', 1.0))
        duty_cycle = float(data.get('duty_cycle', 0.5)) if signal_type == 'square' else None
        sampleRate = int(data.get('sampleRate', 500))

        # 参数验证
        if frequency <= 0 or amplitude <= 0 or duration <= 0 or sampleRate <= 0:
            raise ValueError("Frequency, amplitude, duration, and sample rate must be positive numbers.")
        if signal_type == 'square' and (duty_cycle is None or duty_cycle < 0 or duty_cycle > 1):
            raise ValueError("Duty cycle must be between 0 and 1 for square waves.")

        # 根据信号类型生成信号
        if signal_type == 'sine':
            signal = generate_sine_wave(frequency, amplitude, phase, duration, sampleRate)
        elif signal_type == 'square':
            if duty_cycle is None:
                raise ValueError("Duty cycle is required for square waves.")
            signal = generate_square_wave(frequency, amplitude, duty_cycle, duration, sampleRate)
        elif signal_type == 'triangle':
            signal = generate_triangle_wave(frequency, amplitude, duration, sampleRate)
        else:
            raise ValueError("Unsupported signal type")

        logging.info(
            f"Generated {signal_type} wave with parameters: freq={frequency}, amp={amplitude}, phase={phase}, duration={duration}, sampleRate={sampleRate}"
        )

        return jsonify({
            'message': f'{signal_type.capitalize()} signal generated successfully',
            'signal': signal.tolist(),
            'type': signal_type
        }), 200

    except Exception as e:
        logging.error(f"Error generating signal: {str(e)}")
        return jsonify({'error': str(e)}), 400  # 返回 400 错误码以表示客户端错误

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')


@app.route('/api/process-signal', methods=['POST'])
def process_signal():
    if 'file' not in request.files:
        logging.error('No file part')
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    sampleRate = float(request.form.get('sampleRate', 1000))  # 获取采样率，默认为1000

    if file.filename == '':
        logging.error('No selected file')
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        try:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # 加载数据到numpy数组中
            data = load_data(file_path)

            # 使用 SignalProcessor 处理数据
            processor = SignalProcessor(data, sampleRate=sampleRate)
            results = processor.process_all()

            # 如果有图表需要生成，则在此处处理
            plot_url = generate_plot(results) if isinstance(results, dict) and 'x' in results and 'y' in results else None

            # 返回结果
            response_data = {
                'message': 'Signal processed successfully',
                'results': results,
            }

            if plot_url:
                response_data['plot_url'] = plot_url

            return jsonify(response_data), 200
        except Exception as e:
            logging.error(f"Error processing signal: {str(e)}")
            return jsonify({'error': str(e)}), 500
    else:
        logging.error('File type not allowed')
        return jsonify({'error': 'File type not allowed'}), 400


def load_data(file_path):
    """根据文件扩展名加载数据"""
    file_extension = file_path.lower().rsplit('.', 1)[1]

    if file_extension in ('csv', 'txt'):
        try:
            df = pd.read_csv(file_path)
            # 确保 X 和 Y 列只包含数值数据
            df['X'] = pd.to_numeric(df['X'], errors='coerce')
            df['Y'] = pd.to_numeric(df['Y'], errors='coerce')
            df = df.dropna(subset=['X', 'Y'])

            if df.empty:
                raise ValueError("No valid numeric data found in the file")

            data = {'x': df['X'].values, 'y': df['Y'].values}
        except Exception as e:
            logging.error(f"Error parsing CSV/TXT file {file_path}: {str(e)}")
            raise ValueError(f"Failed to parse CSV/TXT file: {str(e)}")
    elif file_extension == 'xlsx':
        try:
            wb = openpyxl.load_workbook(file_path)
            sheet = wb.active
            data = {'x': [], 'y': []}
            for row in sheet.iter_rows(min_row=2, values_only=True):  # 假设数据从第二行开始
                x, y = row[:2]  # 假设 X 和 Y 数据位于前两列
                if isinstance(x, (int, float)) and isinstance(y, (int, float)):
                    data['x'].append(x)
                    data['y'].append(y)
            data['x'] = np.array(data['x'])
            data['y'] = np.array(data['y'])
        except Exception as e:
            logging.error(f"Error parsing XLSX file {file_path}: {str(e)}")
            raise ValueError(f"Failed to parse XLSX file: {str(e)}")
    elif file_extension == 'xls':
        try:
            wb = xlrd.open_workbook(file_path)
            sheet = wb.sheet_by_index(0)
            data = {'x': [], 'y': []}
            for i in range(1, sheet.nrows):  # 假设数据从第二行开始
                x, y = sheet.row_values(i)[:2]  # 假设 X 和 Y 数据位于前两列
                if isinstance(x, (int, float)) and isinstance(y, (int, float)):
                    data['x'].append(x)
                    data['y'].append(y)
            data['x'] = np.array(data['x'])
            data['y'] = np.array(data['y'])
        except Exception as e:
            logging.error(f"Error parsing XLS file {file_path}: {str(e)}")
            raise ValueError(f"Failed to parse XLS file: {str(e)}")
    elif file_extension == 'dat':
        # 对于 .dat 文件，假设它是二进制数据，这里需要根据实际情况解析
        try:
            with open(file_path, 'rb') as f:
                bytes_data = f.read()
            data = np.frombuffer(bytes_data, dtype=np.float64)  # 根据实际情况调整dtype
        except Exception as e:
            logging.error(f"Error parsing DAT file {file_path}: {str(e)}")
            raise ValueError(f"Failed to parse DAT file: {str(e)}")
    else:
        raise ValueError("Unsupported file extension")

    return data


def generate_plot(results):
    """根据结果生成图表并返回图表URL"""
    try:
        plt.plot(results['x'], results['y'])

        # 将图表保存为 PNG 图像，并将其编码为 Base64 字符串
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        img_str = base64.b64encode(buf.getvalue()).decode('utf-8').replace('\n', '')
        plt.close()

        plot_url = f"data:image/png;base64,{img_str}"
        return plot_url
    except Exception as e:
        logging.error(f"Error generating plot: {str(e)}")
        return None


@app.route('/plot')
def plot():
    plot_url = request.args.get('plot_url')
    if not plot_url:
        return "Plot not available", 400
    return render_template('plot.html', plot_url=plot_url)


if __name__ == '__main__':
    app.run(debug=True)