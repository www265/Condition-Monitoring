from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from flask_cors import CORS
import os
import pandas as pd
import logging
import numpy as np
from datetime import datetime
import openpyxl  # 用于读取 .xlsx 文件
import xlrd  # 用于读取 .xls 文件
from datetime import datetime
from signals import generate_sine_wave, generate_square_wave, generate_triangle_wave

app = Flask(__name__, static_folder='uploads', static_url_path='/uploads')
CORS(app, resources={
    r"/api/*": {"origins": "http://localhost:8080"},
    r"/uploads/*": {"origins": "http://localhost:8080"}
})
# 配置上传目录和允许的文件扩展名
UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = {'csv','txt','xls','xlsx','dat'}
MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 限制文件大小为10MB

if not os.path.exists (UPLOAD_FOLDER):
    os.makedirs (UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# 设置日志配置
logging.basicConfig (filename='app.log', level=logging.INFO)


def allowed_file(filename):
    return '.' in filename and filename.rsplit ('.', 1)[1].lower () in ALLOWED_EXTENSIONS


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
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON data'}), 400

        signal_type = data.get('type', 'sine').lower()
        frequency = float(data.get('frequency', 1.0))
        amplitude = float(data.get('amplitude', 1.0))
        phase = float(data.get('phase', 0.0))
        duration = float(data.get('duration', 1.0))
        duty_cycle = float(data.get('duty_cycle', 0.5))  # 只对方波有效
        SampleRate = float(data.get('SampleRate', 44100))  # 添加默认采样率

        if frequency <= 0 or amplitude <= 0 or duration <= 0 or SampleRate <= 0:
            raise ValueError("Frequency, amplitude, duration, and sample rate must be positive numbers.")

        if signal_type == 'sine':
            signal = generate_sine_wave(frequency, amplitude, phase, duration, SampleRate)
        elif signal_type == 'square':
            signal = generate_square_wave(frequency, amplitude, duty_cycle, duration, SampleRate)
        elif signal_type == 'triangle':
            signal = generate_triangle_wave(frequency, amplitude, duration, SampleRate)
        else:
            raise ValueError("Unsupported signal type")

        logging.info(
            f"Generated {signal_type} wave with parameters: freq={frequency}, amp={amplitude}, phase={phase}, duration={duration}, sample_rate={SampleRate} at {datetime.now()}"
        )

        return jsonify({
            'message': f'{signal_type.capitalize()} signal generated successfully',
            'signal': signal,
            'type': signal_type
        }), 200

    except Exception as e:
        logging.error(f"Error generating signal: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/')
def index():
    return jsonify({
        'message': 'Welcome to the Signal Generator API!',
        'endpoints': {
            'upload': '/upload',
            'generate_signal': '/generate-signal'
        }
    }), 200


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')


if __name__ == '__main__':
    app.run(debug=True)