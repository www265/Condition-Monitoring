<template>
  <div class="signal-generator">
    <h2>Signal Generator</h2>

    <!-- 表单 -->
    <form @submit.prevent="generateSignal" class="signal-form-container">
      <SignalForm
        v-for="(signal, index) in signals"
        :key="index"
        :signal="signal"
        :index="index + 1"
        @input-change="updateSignal"
      />
    </form>

    <!-- 按钮 -->
    <button type="button" @click="generateSignal" class="generate-button">Generate Signal</button>

    <!-- 提示信息 -->
    <p v-if="message">{{ message }}</p>

    <!-- 图表区域 -->
    <div v-if="chartData" class="plot responsive-plot">
      <h4>Data Visualization:</h4>
      <canvas ref="combinedSignalChart"></canvas>
    </div>
  </div>
</template>

<script>
import { reactive } from 'vue';
import axios from 'axios';
import { Chart, registerables } from 'chart.js';
import zoomPlugin from 'chartjs-plugin-zoom';


// 注册 Chart.js 的必要组件
Chart.register(...registerables, zoomPlugin);

// 子组件 SignalForm.vue (假设已经创建)
import SignalForm from './SignalForm.vue';

export default {
  name: 'SignalGenerator',
  components: {
    SignalForm
  },
  setup() {
    // 定义两个信号对象，使用 reactive 包装以确保响应性
    const signals = reactive([
      {
        waveformType: 'sine',
        frequency: 100,
        amplitude: 1,
        phase: 0,
        dutyCycle: 0.5,
        duration: 1,
        sampleRate: 1000,
      },
      {
        waveformType: 'sine',
        frequency: 100,
        amplitude: 1,
        phase: 0,
        dutyCycle: 0.5,
        duration: 1,
        sampleRate: 1000,
      }
    ]);

    return { signals };
  },
  data() {
    return {
      message: '',
      chartData: null,
      chartInstance: null
    };
  },
  methods: {
    updateSignal(updatedSignal, index) {
      // 直接更新对应的信号对象
      this.signals[index - 1] = updatedSignal;
    },
    async generateSignal() {
      try {
        // 确保两个信号的采样率相同
        if (this.signals[0].sampleRate !== this.signals[1].sampleRate) {
          this.message = 'Both signals must have the same sample rate.';
          return;
        }

        const requests = this.signals.map(signal => {
          const params = {
            type: signal.waveformType,
            frequency: signal.frequency,
            amplitude: signal.amplitude,
            phase: signal.phase * Math.PI / 180, // 将度数转换为弧度
            duration: signal.duration,
            sampleRate: parseInt(signal.sampleRate, 10),
          };

          if (signal.waveformType === 'square') {
            params.duty_cycle = signal.dutyCycle;
          }

          return axios.post('http://127.0.0.1:5000/api/generate-signal', params, {
            headers: {
              'Content-Type': 'application/json'
            }
          });
        });

        const responses = await Promise.all(requests);
        const [response1, response2] = responses;

        const { signal: signal1 } = response1.data;
        const { signal: signal2 } = response2.data;

        // 计算叠加信号
        const combinedSignal = signal1.map((value, index) => value + signal2[index]);

        // 生成 x 数据
        const sampleRate = parseInt(this.signals[0].sampleRate, 10);
        const xData = Array.from({ length: combinedSignal.length }, (_, i) => i / sampleRate).filter(label => !isNaN(label));

        // 准备图表数据
        this.chartData = {
          labels: xData,
          datasets: [
            {
              label: `${this.signals[0].waveformType} Signal`,
              data: signal1,
              borderColor: 'rgba(75, 192, 192, 1)',
              fill: false
            },
            {
              label: `${this.signals[1].waveformType} Signal`,
              data: signal2,
              borderColor: 'rgba(255, 99, 132, 1)',
              fill: false
            },
            {
              label: 'Combined Signal',
              data: combinedSignal,
              borderColor: 'rgba(54, 162, 235, 1)',
              fill: false
            }
          ]
        };

        this.message = 'Signals generated successfully!';
        this.$nextTick(() => {
          this.drawChart();
        });
      } catch (error) {
        this.message = 'There was an error generating the signals!';
        console.error('Error:', error);
      }
    },
    drawChart() {
    const canvas = this.$refs.combinedSignalChart;

    // 确保 canvas 存在并且其父容器有明确的尺寸
    if (!canvas || !canvas.parentElement) {
      console.error('Canvas element not found or its parent container is not properly sized.');
      return;
    }

    // 使用 $nextTick 确保 DOM 已更新
    this.$nextTick(() => {
      const ctx = canvas.getContext('2d');

      // 销毁之前的图表实例（如果存在）
      if (this.chartInstance) {
        this.chartInstance.destroy();
      }

      // 创建新的图表实例
      this.chartInstance = new Chart(ctx, {
        type: 'line',
        data: this.chartData,
        options: {
          responsive: true,
          //maintainAspectRatio: false, // 避免不必要的比例保持
          plugins: {
            legend: {
              position: 'top',
            },
            tooltip: {
              mode: 'index',
              intersect: false,
            },
            zoom: {
              pan: {
                enabled: true,
                mode: 'x',
                threshold: 5,
                modifierKey: 'ctrl'
              },
              zoom: {
                wheel: {
                  enabled: true,
                },
                pinch: {
                  enabled: true
                },
                drag: {
                  enabled: true,
                  mode: 'x',
                },
                mode: 'x',
              }
            }
          },
          scales: {
            x: {
              type: 'linear',
              position: 'bottom',
              title: {
                display: true,
                text: 'Time (s)'
              }
            },
            y: {
              title: {
                display: true,
                text: 'Amplitude (V)'
              }
            }
          }
        }
      });
      const resetZoomOnRightClick = (event) => {
        if (event.button === 2) { // 检查是否为右键点击 (button: 2)
          event.preventDefault(); // 阻止默认上下文菜单
          this.chartInstance.resetZoom();
        }
      };

      // 监听图表容器上的右键点击事件
      canvas.addEventListener('contextmenu', resetZoomOnRightClick);

      // 将事件监听器存储以便稍后移除
      this.resetZoomListener = resetZoomOnRightClick;


    });
   }
  },
  beforeUnmount() {
      if (this.chartInstance) {
        // 移除事件监听器
        if (this.resetZoomListener && this.$refs.combinedSignalChart) {
        this.$refs.combinedSignalChart.removeEventListener('contextmenu', this.resetZoomListener);
        }
        // 销毁图表实例
        this.chartInstance.destroy();
        this.chartInstance = null;
      }
  }
};
</script>

<style scoped>
.signal-generator {
  text-align: center;
}

.signal-form-container {
  display: flex;
  justify-content: space-around;
  margin-bottom: 20px;
}

.generate-button {
  padding: 10px 20px;
  background-color: #4CAF50;
  color: white;
  border: none;
  cursor: pointer;
  margin-top: 20px;
}

.generate-button:hover {
  background-color: #45a049;
}

.plot, .responsive-plot {
  width: 100%;
  height: auto;
  position: relative;
}

.plot canvas {
  width: 100%!important;
  height: auto!important;
}
</style>