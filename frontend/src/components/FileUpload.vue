<template>
  <div class="file-upload">
    <h3>Upload a CSV, XLSX, DAT, TXT or Single Line Text File</h3>
    <form @submit.prevent="handleSubmit">
      <input type="file" @change="handleFileChange" accept=".csv,.xlsx,.xls,.txt,.dat" />
      <button type="submit">Upload</button>
    </form>
    <div v-if="preview" class="preview">
      <h4>File Preview:</h4>
      <div v-html="preview"></div>
    </div>
    <div v-if="plotUrl" class="plot">
      <img :src="plotUrl" alt="Data Visualization"/>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'FileUpload',
  data() {
    return {
      file: null,
      preview: null,
      plotUrl: null
    };
  },
  methods: {
    handleFileChange(event) {
      this.file = event.target.files[0];
      this.preview = null;
      this.plotUrl = null;
    },
    async handleSubmit() {
      if (!this.file) {
        alert('请选择一个文件');
        return;
      }

      const formData = new FormData();
      formData.append('file', this.file);

      try {
        const response = await axios.post('http://127.0.0.1:5000/api/upload', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        });

        // 检查响应是否包含 file_path 字段
        if (!response.data || !response.data.file_path) {
          throw new Error("Invalid response from server");
        }

        const { file_path } = response.data;

        // 构建完整的 URL 或相对路径
        const backendBaseUrl = 'http://127.0.0.1:5000/';
        const fullUrl = new URL(file_path, backendBaseUrl).href;

        // 根据文件扩展名调用相应的解析方法
        const ext = this.file.name.split('.').pop().toLowerCase();
        let chartData;

        if (['csv', 'xlsx', 'xls'].includes(ext)) {
          chartData = await this.parseStructuredFile(fullUrl);
        } else if (['txt', 'dat'].includes(ext)) {
          chartData = await this.parseSingleLineTextFile(fullUrl);
        } else {
          throw new Error('Unsupported file format');
        }

        this.$emit('file-uploaded', chartData);
      } catch (error) {
        console.error('Error uploading file:', error.response ? JSON.stringify(error.response) : error.message);
        console.log('Full error object:', error);  // 打印完整的错误对象
        alert(`文件上传失败: ${error.response ? error.response.data.error : error.message}`);
      }
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

    // 检查文件是否为空
    if (!content) {
      throw new Error('File is empty');
    }

    // 定义解析内容的辅助函数
    const parseContent = (delimiter) => {
      return content.split(delimiter).map(item => item.trim()).filter(item => item !== '').map(item => parseFloat(item)).filter(num => !isNaN(num));
    };

    // 判断前3个字符中是否存在逗号
    const useCommaAsDelimiter = content.slice(0, 3).includes(',');

    let data;

    // 根据是否存在逗号选择分隔符
    if (useCommaAsDelimiter) {
      data = parseContent(',');
    } else {
      data = parseContent(/\s+/); // 使用正则表达式匹配一个或多个空格
    }

    // 再次检查是否有有效的数值数据
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
  max-width: 600px;
  margin: auto;
}

.preview {
  margin-top: 20px;
}

.plot img {
  width: 100%;
  height: auto;
}
</style>