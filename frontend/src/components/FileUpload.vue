<template>
  <div class="file-upload">
    <h3>Upload a CSV, XLSX, DAT, TXT or Single Line Text File</h3>
    <form @submit.prevent="handleSubmit">
      <input type="file" @change="handleFileChange" accept=".csv,.xlsx,.xls,.txt,.dat" />
      <button type="submit">Upload and Plot</button>
    </form>
    <div v-if="chartData" class="plot responsive-plot">
      <h4>Data Visualization:</h4>
      <canvas ref="chartCanvas"></canvas>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { Chart, registerables } from 'chart.js';

Chart.register(...registerables);

export default {
  name: 'FileUpload',
  data() {
    return {
      file: null,
      chartInstance: null, // 用于存储 Chart.js 图表实例
      chartData: null, // 存储图表数据
    };
  },
  methods: {
    handleFileChange(event) {
      this.file = event.target.files[0];
      console.log('File selected:', this.file);
    },
    async handleSubmit() {
  console.log('Submit button clicked');

  if (!this.file) {
    alert('请选择一个文件');
    return;
  }

  const formData = new FormData();
  formData.append('file', this.file);

  try {
    console.log('Attempting to upload file...');
    const response = await axios.post('http://127.0.0.1:5000/api/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });

    console.log('Server response:', response.data); // 查看服务器响应

    if (!response.data || !response.data.file_path && !response.data.results) {
      throw new Error("Invalid response from server");
    }

    const { file_path } = response.data;
    const backendBaseUrl = 'http://127.0.0.1:5000/';
    const fullUrl = new URL(file_path, backendBaseUrl).href;

    console.log('Full URL for uploaded file:', fullUrl); // 查看文件URL

    const ext = this.file.name.split('.').pop().toLowerCase();

    if (['csv', 'xlsx', 'xls'].includes(ext)) {
      this.chartData = await this.parseStructuredFile(fullUrl);
    } else if (['txt', 'dat'].includes(ext)) {
      this.chartData = await this.parseSingleLineTextFile(fullUrl);
    } else {
      throw new Error('Unsupported file format');
    }

    console.log('Chart data prepared:', this.chartData); // 查看准备好的图表数据

    this.$nextTick(() => {
      this.updatePreview(this.chartData);
    });
  } catch (error) {
    console.error('Error uploading file:', error.response ? JSON.stringify(error.response) : error.message);
    console.log('Full error object:', error);
    alert(`文件上传失败: ${error.response ? error.response.data.error : error.message}`);
  }
},
    updatePreview(chartData) {
      console.log('Updating chart preview with data:', chartData); // 查看传入的数据

      // 销毁之前的图表实例（如果存在）
      if (this.chartInstance) {
        this.chartInstance.destroy();
      }

      // 创建新的图表实例
      const ctx = this.$refs.chartCanvas?.getContext('2d');
      if (!ctx) {
        console.error('Canvas context not found.');
        return;
      }

      this.chartInstance = new Chart(ctx, {
        type: 'line', // 或者其他类型的图表
        data: {
          labels: chartData.labels,
          datasets: [{
            label: 'Data',
            data: chartData.datasets[0].data,
            borderColor: 'rgba(75, 192, 192, 1)',
            fill: false
          }]
        },
        options: {
          animation: false,
          responsive: true,
          // maintainAspectRatio: false,
          scales: {
            x: {
              title: {
                display: true,
                text: 'X Axis Label'
              }
            },
            y: {
              title: {
                display: true,
                text: 'Y Axis Label'
              }
            }
          }
        }
      });
      console.log('Chart created.');
    },

    async parseStructuredFile(fullUrl) {
      try {
        const response = await axios.get(fullUrl, { responseType: 'text' });
        let lines = response.data.split('\n').filter(line => line.trim() !== '');
        let xData, yData;

        if (lines.length > 0) {
          const headers = lines[0].split(',').map(h => h.trim());
          const xIndex = headers.indexOf('X');
          const yIndex = headers.indexOf('Y');

          if (xIndex === -1 || yIndex === -1) {
            throw new Error("Invalid file format: Missing X or Y column");
          }

          xData = lines.slice(1).map(line => parseFloat(line.split(',')[xIndex]));
          yData = lines.slice(1).map(line => parseFloat(line.split(',')[yIndex]));
        } else {
          throw new Error("File is empty or contains no valid data");
        }

        return { labels: xData, datasets: [{ data: yData }] };
      } catch (error) {
        console.error('Error parsing structured file:', error.message);
        throw error;
      }
    },
    async parseSingleLineTextFile(fullUrl) {
      try {
        const response = await axios.get(fullUrl, { responseType: 'text' });
        let content = response.data.trim();

        if (!content) {
          throw new Error('File is empty');
        }

        const parseContent = (delimiter) => {
          return content.split(delimiter).map(item => item.trim()).filter(item => item !== '').map(item => parseFloat(item)).filter(num => !isNaN(num));
        };

        const useCommaAsDelimiter = content.slice(0, 3).includes(',');

        let data;

        if (useCommaAsDelimiter) {
          data = parseContent(',');
        } else {
          data = parseContent(/\s+/); // 使用正则表达式匹配一个或多个空格
        }

        if (data.length === 0) {
          throw new Error('File does not contain any numeric data');
        }

        return {
          labels: Array.from({ length: data.length }, (_, i) => i),
          datasets: [{
            label: 'Single Line Text Data',
            data,
            borderColor: 'rgba(75, 192, 192, 1)',
            fill: false,
          }]
        };
      } catch (error) {
        console.error('Error parsing single line text file:', error.message);
        throw error;
      }
    }
  }

};
</script>

<style scoped>
.file-upload {
  max-width: 100%;
  margin: auto;
}

.plot, .responsive-plot {
  margin-top: 20px;
  width: 100%; /* 确保 plot 容器占据所有可用宽度 */
  position: relative; /* 确保 canvas 相对于这个容器定位 */
}

.plot canvas {
  width: 100%!important; /* 强制 canvas 宽度为 100% */
  height: auto!important; /* 高度自适应 */
}
</style>