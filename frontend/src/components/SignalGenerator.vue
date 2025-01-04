<template>
  <div class="signal-generator">
    <h2>Signal Generator</h2>
    <form @submit.prevent="generateSignal">
      <!-- 波形选择 -->
      <label for="waveform">Waveform Type:</label>
      <select id="waveform" v-model="waveformType">
        <option value="sine">Sine Wave</option>
        <option value="square">Square Wave</option>
        <option value="triangle">Triangle Wave</option>
      </select>

      <!-- 频率设置 -->
      <label for="frequency">Frequency (Hz):</label>
      <input type="number" id="frequency" v-model="frequency" required />

      <!-- 幅度设置 -->
      <label for="amplitude">Amplitude (V):</label>
      <input type="number" id="amplitude" v-model="amplitude" step="0.01"required />

      <!-- 相位设置 -->
      <label for="phase">Phase (degrees):</label>
      <input type="number" id="phase" v-model="phase" required />

      <!-- 采样率设置 -->
      <label for="sampleRate">SampleRate (Hz):</label>
      <input type="number" id="sampleRate" v-model="sampleRate" required min="1" placeholder="512000">

      <!-- 占空比仅对方波有效 -->
      <div v-if="waveformType === 'square'">
        <label for="duty-cycle">Duty Cycle (0 to 1):</label>
        <input type="number" id="duty-cycle" v-model="dutyCycle" step="0.01" min="0" max="1" required />
      </div>

      <!-- 持续时间 -->
      <label for="duration">Duration (seconds):</label>
      <input type="number" id="duration" v-model="duration" step="0.01" required />

      <button type="submit">Generate Signal</button>
    </form>

    <!-- 提示信息 -->
    <p v-if="message">{{ message }}</p>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'SignalGenerator', // 修正拼写错误
  data() {
    return {
      waveformType: 'sine',
      frequency: 1000, // 默认值为1kHz
      amplitude: 1, // 默认幅度为1V
      phase: 0, // 默认相位为0度
      dutyCycle: 0.5, // 方波默认占空比为50%
      duration: 1, // 默认持续时间为1秒
      sampleRate: 1000, // 默认采样率为512000 Hz
      signalData: null,
      message: ''
    };
  },
  methods: {
    async generateSignal() {
      try {
        // 保存原始值
        const originalFrequency = parseFloat(this.frequency).toFixed(2);
        const originalSampleRate = parseInt(this.sampleRate, 10);
        // 验证采样率是否有效
        if (!this.sampleRate || this.sampleRate <= 0) {
          console.error('Invalid Sample rate provided. Using default value.');
          this.sampleRate = 1000; // 使用默认采样率
        }

        const response = await axios.post('http://127.0.0.1:5000/api/generate-signal', {
        type: this.waveformType,
        frequency: parseFloat(this.frequency),
        amplitude: parseFloat(this.amplitude),
        phase: this.phase * Math.PI / 180, // 将度数转换为弧度
        duty_cycle: this.dutyCycle,
        duration: parseFloat(this.duration),
        sampleRate: parseInt(this.sampleRate, 10)
      }, {
          headers: {
            'Content-Type': 'application/json'
          }
        });

        const { signal, type } = response.data;

        // 过滤掉 NaN 值

        // 打印调试信息
        console.log(`Sample Rate: ${this.sampleRate}`);
        console.log('Generating signal with parameters:', {
          type: this.waveformType,
          frequency: this.frequency,
          amplitude: this.amplitude,
          phase: this.phase,
          duty_cycle: this.dutyCycle,
          duration: this.duration,
          sampleRate: this.sampleRate // 使用统一的小写命名
        });

        // 确保 xData 和 cleanedSignal 长度一致
        const xData = Array.from({ length: signal.length }, (_, i) => {
          const label = i / this.sampleRate;
          if (isNaN(label)) {
            console.error(`Generated NaN at index ${i}, SampleRate: ${this.sampleRate}`);
          }
          return label;
        }).filter(label => !isNaN(label)); // 再次过滤掉任何可能产生的 NaN

        // 发送清理后的数据给父组件
        this.$emit('signal-generated', {
          labels: xData,
          datasets: [{
            data: signal,
            label: `${this.waveformType} Signal`,
            borderColor: 'rgba(75, 192, 192, 1)',
            fill: false
          }]
        });

        this.signalData = JSON.stringify(response.data, null, 2);
        // 恢复原始值
        this.frequency = originalFrequency;
        this.sampleRate = originalSampleRate;
        this.message = `${this.waveformType} signal generated successfully!`;
      } catch (error) {
        this.message = 'There was an error generating the signal!';
        console.error('Error:', error);
      }
    }
  }
};
</script>

<style scoped>
/* 样式可以根据实际需求调整 */
.signal-generator {
  text-align: center;
}

form {
  display: inline-block;
  text-align: left;
  margin-top: 20px;
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
}

button:hover {
  background-color: #45a049;
}
</style>