<template>
  <div class="home">
    <h1>Home</h1>
    <div v-if="tab === 'upload'">
      <h2>Upload File</h2>
      <input type="file" @change="onFileSelected" />
      <button @click="uploadFile">Upload</button>
      <p v-if="message">{{ message }}</p>
      <progress v-if="uploading" :value="progress" max="100"></progress>

      <!-- 添加 LineChart 组件 -->
      <line-chart :chartdata="chartData" v-if="chartData"></line-chart>
    </div>
    <div v-else-if="tab === 'generator'">
      <h2>Signal Generator</h2>
      <form @submit.prevent="generateSignal">
        <label for="signal-type">Signal Type:</label>
        <select id="signal-type" v-model="signalType">
          <option value="sine">Sine Wave</option>
          <option value="square">Square Wave</option>
          <option value="triangle">Triangle Wave</option>
        </select>

        <label for="frequency">Frequency (Hz):</label>
        <input type="number" id="frequency" v-model="frequency" required />

        <label for="amplitude">Amplitude:</label>
        <input type="number" id="amplitude" v-model="amplitude" required />

        <label for="phase">Phase (radians):</label>
        <input type="number" id="phase" v-model="phase" required />

        <label for="SampleRate">采样率 (Hz):</label>
        <input id="SampleRate" v-model.number="SampleRate" type="number" min="1" placeholder="512000">

        <div v-if="signalType === 'square'">
          <label for="duty-cycle">Duty Cycle (0 to 1):</label>
          <input type="number" id="duty-cycle" v-model="dutyCycle" step="0.01" min="0" max="1" required />
        </div>

        <label for="duration">Duration (seconds):</label>
        <input type="number" id="duration" v-model="duration" required />

        <button type="submit">Generate Signal</button>
      </form>

      <div v-if="signalData">
        <h3>Generated {{ capitalizeFirstLetter(signalType) }} Signal Data:</h3>
        <pre>{{ signalData }}</pre>
      </div>

      <p v-if="message">{{ message }}</p>

      <!-- 添加 LineChart 组件 -->
      <line-chart :chartdata="chartData" v-if="chartData"></line-chart>
    </div>
    <button @click="switchTab">{{ tab === 'upload' ? 'Switch to Signal Generator' : 'Switch to Upload' }}</button>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import axios from 'axios';
import LineChart from './components/LineChart.vue';

const tab = ref('upload');
const selectedFile = ref(null);
const uploading = ref(false);
const progress = ref(0);
const message = ref('');
const signalType = ref('sine');
const frequency = ref(1.0);
const amplitude = ref(1.0);
const phase = ref(0.0);
const dutyCycle = ref(0.5);
const duration = ref(1.0);
const SampleRate = ref(512000);
const signalData = ref(null);
const chartData = ref(null);

function onFileSelected(event) {
  selectedFile.value = event.target.files[0];
  message.value = ''; // 清除之前的提示信息
  if (selectedFile.value && selectedFile.value.size > 10 * 1024 * 1024) {
    message.value = 'File size exceeds the limit of 10MB';
    selectedFile.value = null;
  }
}

async function uploadFile() {
  if (!selectedFile.value) {
    alert('请选择一个文件');
    return;
  }

  const formData = new FormData();
  formData.append('file', selectedFile.value);

  try {
    const response = await axios.post('http://127.0.0.1:5000/api/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });

    // 假设服务器返回的数据可以直接用于图表渲染
    chartData.value = response.data;
    message.value = '文件上传成功！';
  } catch (error) {
    handleAxiosError(error);
  }
}

async function generateSignal() {
  try {
    // 验证采样率是否有效
    if (!SampleRate.value || SampleRate.value <= 0) {
      alert('请提供一个有效的采样率 (大于0)');
      return;
    }

    const response = await axios.post('http://127.0.0.1:5000/api/generate-signal', {
      type: signalType.value,
      frequency: frequency.value,
      amplitude: amplitude.value,
      phase: phase.value * Math.PI / 180, // 将度数转换为弧度
      duty_cycle: dutyCycle.value,
      duration: duration.value,
      SampleRate: SampleRate.value
    }, {
      headers: {
        'Content-Type': 'application/json'
      }
    });

    const { signal } = response.data;

    // 过滤掉 NaN 值
    const cleanedSignal = signal.filter(dataPoint => !isNaN(dataPoint));

    // 确保 xData 和 cleanedSignal 长度一致
    const xData = Array.from({ length: cleanedSignal.length }, (_, i) => i / SampleRate.value);

    chartData.value = {
      labels: xData,
      datasets: [{
        data: cleanedSignal,
        label: `${capitalizeFirstLetter(signalType.value)} Signal`,
        borderColor: 'rgba(75, 192, 192, 1)',
        fill: false
      }]
    };

    signalData.value = JSON.stringify(response.data, null, 2);
    message.value = `${capitalizeFirstLetter(signalType.value)} signal generated successfully!`;
  } catch (error) {
    handleAxiosError(error);
  }
}

function switchTab() {
  tab.value = tab.value === 'upload' ? 'generator' : 'upload';
}

function capitalizeFirstLetter(string) {
  return string.charAt(0).toUpperCase() + string.slice(1);
}

function handleAxiosError(error) {
  message.value = 'There was an error!';
  console.error('Error:', error);
  if (error.response) {
    message.value = `Error: ${error.response.data.error}`;
  } else if (error.request) {
    message.value = 'Network request failed, please check your connection.';
  } else {
    message.value = 'An error occurred during processing.';
  }
}
</script>

<style scoped>
/* 保持原有样式 */
.home {
  text-align: center;
  margin-top: 50px;
}

form {
  display: inline-block;
  text-align: left;
}

label {
  display: block;
  margin-bottom: 8px;
}

input, select {
  margin-bottom: 20px;
  padding: 5px;
  width: 100%;
}

button {
  padding: 10px 20px;
  background-color: #4CAF50;
  color: white;
  border: none;
  cursor: pointer;
  margin-top: 20px;
}

button:hover {
  background-color: #45a049;
}

progress {
  width: 80%;
  margin: 20px auto;
}
</style>