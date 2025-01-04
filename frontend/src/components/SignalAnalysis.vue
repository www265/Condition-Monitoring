<template>
  <div class="signal-analysis">
    <h3>Signal Analysis</h3>
    <form @submit.prevent="handleSubmit">
      <label for="sample-rate">Sample Rate (Hz):</label>
      <input id="sample-rate" v-model="sampleRate" type="number" step="any" required />
      <button type="submit">Draw Data</button>
    </form>

    <div v-if="charts.length" class="charts">
      <div v-for="(chart, index) in charts" :key="index" class="chart-container">
        <h4>{{ chart.title }}</h4>
        <canvas :id="`chart-${index}`"></canvas>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import Chart from 'chart.js/auto';

export default {
  name: 'SignalAnalysis',
  inject: ['fileData'], // 注入父组件提供的文件数据
  data() {
    return {
      sampleRate: 1000,
      charts: []
    };
  },
  methods: {
    async handleSubmit() {
      const fileDataValue = this.fileData;

      if (!fileDataValue) {
        alert('No data to analyze');
        return;
      }

      try {
        this.charts = [];
        const response = await axios.post('http://127.0.0.1:5000/api/process_signal', { data: fileDataValue, sample_rate: this.sampleRate });

        this.charts = [
          { title: 'Original Data', data: response.data.original_data },
          { title: 'Original Spectrum', data: response.data.original_spectrum },
          { title: 'Integrated Waveform', data: response.data.integrated_data },
          { title: 'Integrated Spectrum', data: response.data.integrated_spectrum },
          { title: 'Envelope Demodulated Waveform', data: response.data.envelope_data },
          { title: 'Envelope Demodulated Spectrum', data: response.data.envelope_spectrum }
        ];

        this.renderCharts();
      } catch (error) {
        console.error('Error processing signal:', error.message);
        alert('信号处理失败');
      }
    },
    renderCharts() {
      this.charts.forEach((chart, index) => {
        const ctx = document.getElementById(`chart-${index}`).getContext('2d');
        new Chart(ctx, {
          type: 'line',
          data: {
            labels: Array.from({ length: chart.data.x ? chart.data.x.length : chart.data.length }, (_, i) => i),
            datasets: [{
              label: chart.title,
              data: chart.data.y ? chart.data.y : chart.data,
              borderColor: 'rgba(75, 192, 192, 1)',
              fill: false
            }]
          }
        });
      });
    }
  }
};
</script>

<style scoped>
.signal-analysis {
  max-width: 800px;
  margin: auto;
}

.chart-container {
  margin-top: 20px;
}
</style>