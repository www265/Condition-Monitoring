<template>
  <div id="app" class="container">
    <!-- 左面板 -->
    <div class="panel left-panel">
      <div class="upper-section">
        <h2>上传文件并绘制数据</h2>
        <FileUpload @file-uploaded="handleFileUploaded" />
      </div>
      <div class="lower-section" v-if="fileChartData">
        <h3>上传文件后的XY数据图</h3>
        <LineChart :chartData="fileChartData" />
      </div>
      <div v-else-if="fileError" class="error-message">
        <p>{{ fileError }}</p>
      </div>
      <div v-else class="loading">正在加载...</div>
    </div>

    <!-- 右面板 -->
    <div class="panel right-panel">
      <div class="upper-section">
        <h2>信号发生器</h2>
        <SignalGenerator @signal-generated="handleSignalGenerated" />
      </div>
      <div class="lower-section" v-if="signalChartData">
        <h3>信号发生器获取的数据图</h3>
        <LineChart :chartData="signalChartData" />
      </div>
      <div v-else-if="signalError" class="error-message">
        <p>{{ signalError }}</p>
      </div>
      <div v-else class="loading">正在加载...</div>
    </div>
  </div>
</template>

<script>
import FileUpload from './components/FileUpload.vue';
import SignalGenerator from './components/SignalGenerator.vue';
import LineChart from './components/LineChart.vue';

export default {
  name: 'App',
  components: {
    FileUpload,
    SignalGenerator,
    LineChart
  },
  data() {
    return {
      fileChartData: null,
      signalChartData: null,
      fileError: null,
      signalError: null,
    };
  },
  methods: {
    handleFileUploaded(data, error) {
      if (error) {
        this.fileError = error;
        this.fileChartData = null;
      } else {
        this.fileError = null;
        this.fileChartData = data;
      }
    },
    handleSignalGenerated(data, error) {
      if (error) {
        this.signalError = error;
        this.signalChartData = null;
      } else {
        this.signalError = null;
        this.signalChartData = data;
      }
    }
  }
};
</script>

<style scoped>
.container {
  display: flex;
}

.panel {
  width: 50%;
  padding: 20px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.left-panel {
  background-color: #f4f4f4;
}

.right-panel {
  background-color: #e9e9e9;
}

.upper-section, .lower-section {
  padding: 10px;
}

.lower-section {
  border-top: 1px solid #ccc;
}

.loading, .error-message {
  text-align: center;
  padding: 20px;
}
.error-message p {
  color: red;
}
</style>