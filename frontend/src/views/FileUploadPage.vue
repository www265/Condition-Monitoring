<template>
  <div>
    <file-upload @file-uploaded="handleFileUploaded"></file-upload>
    <line-chart :chartData="chartData" v-if="chartData"></line-chart>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import FileUpload from '../components/FileUpload.vue';
import LineChart from '../components/LineChart.vue';

const chartData = ref(null);

function handleFileUploaded(data) {
  chartData.value = data;
}
</script>