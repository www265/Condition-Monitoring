<template>
  <div>
    <signal-generator @signal-generated="handleSignalGenerated"></signal-generator>
    <line-chart :chartData="chartData" v-if="chartData"></line-chart>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import SignalGenerator from '../components/SignalGenerator.vue';
import LineChart from '../components/LineChart.vue';

const chartData = ref(null);


function handleSignalGenerated(data) {
  chartData.value = data;
}
</script>