<template>
  <div>
    <canvas ref="canvas"></canvas>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick } from 'vue';
import { Chart, registerables } from 'chart.js';

// 显式注册所有默认的 Chart.js 组件
Chart.register(...registerables);

const props = defineProps({
  chartData: {
    type: Object,
    required: true,
    validator: (value) => typeof value === 'object' && !Array.isArray(value) && value.labels && value.datasets
  }
});

const canvas = ref(null);
let chartInstance = null;

// 挂载时初始化图表
onMounted(() => {
  // 确保 DOM 更新完成后再尝试获取 canvas
  nextTick().then(() => {
    if (canvas.value && props.chartData) {
      renderChart(props.chartData);
    }
  });
});

function renderChart(data) {
  if (!canvas.value || !data) {
    console.error('Canvas element or data is not available.');
    return;
  }

  const ctx = canvas.value.getContext('2d');
  if (!ctx) {
    console.error('Cannot get canvas context.');
    return;
  }

  // 确保旧的图表实例被销毁
  destroyChart();

  try {
    chartInstance = new Chart(ctx, {
      type: 'line',
      data: data,
      options: {
        responsive: true,
        maintainAspectRatio: false, // 确保响应式布局
        plugins: {
          title: {
            display: true,
            text: '原始数据', // 设置图表标题
            font: {
              size: 20 // 设置标题字体大小
            }
          }
        },
        scales: {
          x: {
            title: {
              display: true,
              text: 'Times'
            },
            ticks: {
              callback: function(value, index) {
                // 控制 X 轴标签显示频率
                return index % 10 === 0 ? value : '';
              }
            },
            min: 0,
            type: 'linear' // 确保使用线性刻度
          },
          y: {
            title: {
              display: true,
              text: 'Value'
            },
          ticks: {
            callback: function(value, index, ticks) {
            return parseFloat(value).toFixed(3);
            }
          }
          }
        }
      }
    });

    // 应用于所有数据集的线条样式
    chartInstance.data.datasets.forEach((dataset) => {
      dataset.tension = 0.4;
      dataset.borderWidth = 2;
      dataset.borderColor = '#3cba9f'; // 更改线条颜色
    });

    console.log('Chart instance created successfully:', chartInstance);
  } catch (error) {
    console.error('Failed to create chart instance:', error);
  }
}

async function updateChart(newData) {
  console.log('Updating chart with:', newData); // 日志输出以确认数据
  if (chartInstance && canvas.value) {
    try {
      chartInstance.data = newData;
      chartInstance.update();
      console.log('Chart updated successfully');
    } catch (error) {
      console.error('Failed to update chart:', error);
    }
  } else if (canvas.value) {
    await renderChart(newData);
  }
}

function destroyChart() {
  if (chartInstance) {
    chartInstance.destroy();
    chartInstance = null;
  }
}

// 监听 chartData 的变化
watch(() => props.chartData, async (newVal) => {
  console.log('chartData changed to:', newVal); // 日志输出以确认变化
  if (newVal && Object.keys(newVal).length > 0 && canvas.value) {
    await nextTick(); // 确保 DOM 更新完成
    await updateChart(newVal);
  }
}, { immediate: true });

</script>

<style scoped>
canvas {
  width: 100% !important;
  height: 400px !important;
}
</style>