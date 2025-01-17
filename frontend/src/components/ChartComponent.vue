<template>
  <div>
    <canvas ref="chart" class="chart-canvas"></canvas>
  </div>
</template>

<script>
import { onMounted, ref, watch } from 'vue';
import { Chart, registerables } from 'chart.js';

// Register all the required components for Chart.js
Chart.register(...registerables);

export default {
  name: 'ChartComponent',
  props: {
    chartData: {
      type: Object,
      required: true,

    },
    options: {
      type: Object,
      default: () => ({})
    }
  },
  setup(props) {
    const chart = ref(null);
    let chartInstance = null;

    const renderChart = (data, opts) => {
      if (chartInstance) {
        chartInstance.destroy();
      }

      chartInstance = new Chart(chart.value, {
        type: 'scatter', // or any other chart type you want to use
        data: data,
        options: opts
      });
    };

    onMounted(() => {
      renderChart(props.chartData, props.options);
    });

    watch(
      () => [props.chartData, props.options],
      ([newChartData, newOptions]) => {
        renderChart(newChartData, newOptions);
      }
    );

    return {
      chart
    };
  }
};
</script>

<style scoped>
.chart-canvas  {
  width: 100%;
  height: auto;
  min-height: 400px;
}
/* Add any specific styles for the chart if needed */
canvas {
  max-width: 80%;
  margin: auto;
}
</style>