<template>
  <div class="signal-form-group">
    <h3>Signal {{ index }}</h3>
    <label for="waveform">Waveform Type:</label>
    <select id="waveform" v-model="localSignal.waveformType">
      <option value="sine">Sine Wave</option>
      <option value="square">Square Wave</option>
      <option value="triangle">Triangle Wave</option>
    </select>

    <label for="frequency">Frequency (Hz):</label>
    <input type="number" id="frequency" v-model.number="localSignal.frequency" required />

    <label for="amplitude">Amplitude (V):</label>
    <input type="number" id="amplitude" v-model.number="localSignal.amplitude" step="0.01" required />

    <label for="phase">Phase (degrees):</label>
    <input type="number" id="phase" v-model.number="localSignal.phase" required />

    <label for="sampleRate">Sample Rate (Hz):</label>
    <input type="number" id="sampleRate" v-model.number="localSignal.sampleRate" required min="1" placeholder="512000">

    <div v-if="localSignal.waveformType === 'square'">
      <label for="duty-cycle">Duty Cycle (0 to 1):</label>
      <input type="number" id="duty-cycle" v-model.number="localSignal.dutyCycle" step="0.01" min="0" max="1" required />
    </div>

    <label for="duration">Duration (seconds):</label>
    <input type="number" id="duration" v-model.number="localSignal.duration" step="0.01" required />
  </div>
</template>

<script>
export default {
  props: {
    signal: Object,
    index: Number
  },
  data() {
    return {
      localSignal: { ...this.signal }
    };
  },
  watch: {
    localSignal: {
      handler(newValue) {
        this.$emit('input-change', newValue, this.index);
      },
      deep: true
    }
  }
};
</script>

<style scoped>
.signal-form-group {
  border: 1px solid #ccc;
  padding: 10px;
  width: 45%; /* 设置宽度以使两个表单并列 */
  box-sizing: border-box;
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
</style>