<template>
  <div>
    <!-- 文件上传和参数设置 -->
    <div style="display: flex; align-items: center;">
      <!-- 文件上传 -->
      <div style="margin-right: 10px;">
        <label for="fileUpload">上传文件:</label><br>
        <input type="file" id="fileUpload" multiple @change="handleFileUpload" />
      </div>

      <!-- 输入组：采样频率 -->
      <div style="margin-right: 10px;">
        <label for="sampleRate">采样频率 (Hz):</label><br>
        <input type="number" id="sampleRate" v-model.number="sampleRate" required />
      </div>

      <!-- 输入组：高通截止频率 -->
      <div style="margin-right: 10px;">
        <label for="highPassCutoff">高通截止频率 (Hz):</label><br>
        <input type="number" id="highPassCutoff" v-model.number="highPassCutoff" required />
      </div>

      <!-- 按钮 -->
      <div>
        <button type="button" :disabled="!isDataReady" @click="processSignal"
                class="btn btn-primary"
                style="min-width: 100px; white-space: nowrap;">
          处理信号
        </button>
      </div>
    </div>

    <!-- 图表展示区域 -->
    <div v-if="chartData" style="display: flex; flex-direction: column; align-items: flex-start; margin-top: 20px;">
      <canvas id="original-data-chart" width="800" height="200"></canvas>
      <canvas id="original-spectrum-chart" width="800" height="200"></canvas>
      <canvas id="integrated-data-chart" width="800" height="200"></canvas>
      <canvas id="integrated-spectrum-chart" width="800" height="200"></canvas>
      <canvas id="envelope-data-chart" width="800" height="200"></canvas>
      <canvas id="envelope-spectrum-chart" width="800" height="200"></canvas>
    </div>

    <!-- LineChart 组件用于显示图表数据 -->
    <line-chart :chart-data="chartData" v-if="chartData"></line-chart>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue';
import axios from 'axios';
import { Chart, registerables } from 'chart.js';
Chart.register(...registerables);

// 定义响应式数据
const sampleRate = ref(1000);
const highPassCutoff = ref(100);
const isDataReady = ref(false);
const chartData = ref(null);
const processingResult = ref(null);
let charts = {};
const fileContents = ref([]);

onMounted(() => {
  // 移除了对 EventBus 的依赖
});

onBeforeUnmount(() => {
  destroyCharts();
});

const getRandomColor = () => '#' + Math.floor(Math.random() * 16777215).toString(16);

const getTransparentColor = (color) => color.replace(')', ',0.2)').replace('rgb', 'rgba');

// 文件上传处理
const handleFileUpload = async (event) => {
  const files = event.target.files;
  if (!files.length) {
    console.log('No files selected');
    return;
  }

  const fileContentPromises = Array.from(files).map(file => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();

      reader.onload = function(e) {
        const content = e.target.result.trim(); // 获取文件内容
        // 使用正则表达式来匹配逗号或空格分隔的数据点，并转换为浮点数数组
        const dataPoints = content.split(/[\s,]+/).map(Number).filter(value => !isNaN(value));
        console.log(`Loaded file: ${file.name}, Data points count: ${dataPoints.length}`);
        resolve(dataPoints); // 返回数据点数组
      };

      reader.onerror = function(error) {
        console.error(`Failed to read file: ${file.name}`, error);
        reject(new Error(`Failed to read file: ${file.name}`));
      };

      reader.readAsText(file);
    });
  });

  try {
    const fileContentArray = await Promise.all(fileContentPromises);
    // 合并所有文件的数据点到一个数组中
    fileContents.value = fileContentArray.flat();
    console.log('All files loaded:', fileContents.value);

    // 检查是否有足够的数据点
    const minDataPointsRequired = 19; // 根据服务器端要求设置最小数据点数
    if (fileContents.value.length < minDataPointsRequired) {
      alert(`需要至少 ${minDataPointsRequired} 个数据点进行信号处理，但只提供了 ${fileContents.value.length} 个。`);
      isDataReady.value = false;
    } else {
      isDataReady.value = true;
    }

    console.log('isDataReady set to', isDataReady.value);
  } catch (error) {
    console.error('Error loading files:', error);
  }
};

const processSignal = async () => {
  try {
    if (!fileContents.value.length || !Array.isArray(fileContents.value)) {
      alert('No valid data available for processing');
      return;
    }

    const nyquistFreq = 0.5 * sampleRate.value;
    if (!(0 < highPassCutoff.value < nyquistFreq)) {
      alert(`Invalid high-pass cutoff frequency: ${highPassCutoff.value}. Must be between 0 and ${nyquistFreq} Hz.`);
      return;
    }

    const postData = {
      data: {
        x: fileContents.value.map((_, index) => index), // 假设x轴是基于索引
        y: fileContents.value // 已经确保所有值都是有效数字
      },
      sample_rate: sampleRate.value,
      high_pass_cutoff: highPassCutoff.value
    };

    console.log('Sending POST request with data:', postData);

    const response = await axios.post('http://127.0.0.1:5000/api/process-signal', postData, {
      headers: {
        'Content-Type': 'application/json'
      }
    });

    if (response.status !== 200 || !response.data || !response.data.results) {
      throw new Error(`Server returned unexpected status code or invalid data: ${response.statusText}`);
    }

    processingResult.value = response.data.results;

    console.log('Processing result received:', processingResult.value);

    // 使用 nextTick 来确保 DOM 更新完成后再绘制图表
    await nextTick();
    drawCharts();

  } catch (error) {
    console.error('Error processing signal:', error);
    console.error('Full error object:', error.response ? JSON.stringify(error.response, null, 2) : error.message);

    let errorMessage = '信号处理失败，请检查控制台日志获取更多信息';
    if (error.response && error.response.data) {
      errorMessage = error.response.data.message || '服务器返回了一个错误响应';
    }

    alert(errorMessage);
  }
};

const drawCharts = async () => {
  console.log('Starting to draw charts...');

  destroyCharts(); // 先销毁旧图表

  const chartMappings = [
    { id: 'original-data-chart', label: 'Original Data', dataKey: 'original_data' },
    { id: 'original-spectrum-chart', label: 'Original Spectrum', dataKey: 'original_spectrum' },
    { id: 'integrated-data-chart', label: 'Integrated Data', dataKey: 'integrated_data' },
    { id: 'integrated-spectrum-chart', label: 'Integrated Spectrum', dataKey: 'integrated_spectrum' },
    { id: 'envelope-data-chart', label: 'Envelope Data', dataKey: 'envelope_data' },
    { id: 'envelope-spectrum-chart', label: 'Envelope Spectrum', dataKey: 'envelope_spectrum' }
  ];

  chartMappings.forEach(({ id, label, dataKey }) => {
    const canvasElement = document.getElementById(id);
    if (!canvasElement) {
      console.error(`Canvas element with id ${id} not found!`);
      return;
    }

    const ctx = canvasElement.getContext('2d');
    if (!ctx) {
      console.error(`Canvas context for ${id} not found!`);
      return;
    }

    let data = [];

    if (processingResult.value && processingResult.value[dataKey]) {
      const resultData = processingResult.value[dataKey];

      // 确保 x 和 y 数据存在并且长度一致
      if (Array.isArray(resultData.y) && Array.isArray(resultData.x) && resultData.y.length === resultData.x.length) {
        data = resultData.y.map((value, index) => ({ x: resultData.x[index], y: value }));
      } else {
        console.warn(`Mismatch in data lengths for ${dataKey}. Using empty dataset.`);
      }
    } else {
      console.warn(`No data available for ${dataKey}. Using empty dataset.`);
    }

    console.log(`Data for ${label}:`, data);

    const chartConfig = {
      type: 'line',
      data: {
        datasets: [{
          label,
          data,
          borderColor: getTransparentColor(getRandomColor()),
          backgroundColor: getTransparentColor(getRandomColor()),
          fill: false
        }]
      },
      options: {
        responsive: true,
        scales: {
          x: {
            type: 'linear',
            position: 'bottom'
          },
          y: {
            beginAtZero: true,
            min: data.length ? Math.min(...data.map(d => d.y)) - 0.1 * Math.abs(Math.min(...data.map(d => d.y))) : 0,
            max: data.length ? Math.max(...data.map(d => d.y)) + 0.1 * Math.abs(Math.max(...data.map(d => d.y))) : 1
          }
        }
      }
    };

    charts[id] = new Chart(ctx, chartConfig);
  });

  console.log('Charts drawn successfully.');

  // 使用 nextTick 确保图表绘制完成后更新响应式数据
  await nextTick();
  chartData.value = processingResult.value.original_data;
};

const destroyCharts = () => {
  Object.keys(charts).forEach(key => {
    if (charts[key]) {
      charts[key].destroy();
      delete charts[key];
    }
  });
};
</script>