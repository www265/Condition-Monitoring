<template>
  <div>
    <signal-analysis @signal-analysised="handleSignalAnalysised"></signal-analysis>
    <line-chart :chartData="chartData" v-if="chartData"></line-chart>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import SignalAnalysis from '../components/SignalAnalysis.vue';
import LineChart from '../components/LineChart.vue';

const chartData = ref(null);


function handleSignalAnalysised(data) {
  chartData.value = data;
}
</script>