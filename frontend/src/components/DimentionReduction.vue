<template>
  <div class="container mt-5">
    <h1 class="text-center mb-4">Dimention Reduction</h1>
    <form @submit.prevent="applyDimentionalityReduction" class="mb-4">
      <div class="form-group">
        <label for="algorithm">Algorithm:</label>
        <select id="algorithm" v-model="selectedAlgorithm" class="form-control">
          <option value="PCA" title="主成分分析是一种统计过程，用来识别不同变量之间的线性关系，以及这些变量如何共同变化以解释观察到的数据变异。">PCA (Principal Component Analysis - 主成分分析)</option>
          <option value="LDA" title="线性判别分析是一种方法，用于寻找能够最好地区分两个或多个类别的特征子空间。">LDA (Linear Discriminant Analysis - 线性判别分析)</option>
          <option value="KernelPCA" title="核主成分分析是主成分分析的非线性扩展，通过应用核技巧来处理非线性数据。">KernelPCA (Kernel Principal Component Analysis - 核主成分分析)</option>
          <option value="ICA" title="独立成分分析是一种多变量统计技术，用于揭示随机变量、测量或信号集中的隐藏因素。">ICA (Independent Component Analysis - 独立成分分析)</option>
          <option value="FA" title="因子分析是一种统计方法，旨在发现大量变量中潜在的结构。">FA (Factor Analysis - 因子分析)</option>
          <option value="tSNE" title="t-SNE 是一种概率模型，它在低维空间中保持点与点之间的距离，从而实现高维数据的可视化。">tSNE (t-distributed Stochastic Neighbor Embedding - t-分布随机邻域嵌入)</option>
          <option value="MDS" title="多维缩放是一种技术，用于根据对象之间的距离创建低维表示。">MDS (Multidimensional Scaling - 多维缩放)</option>
          <option value="LLE" title="局部线性嵌入是一种非线性降维方法，它保留了数据点的局部几何特性。">LLE (Locally Linear Embedding - 局部线性嵌入)</option>
          <option value="SVD" title="奇异值分解是一种矩阵分解方法，广泛应用于数据压缩和降维。">SVD (Singular Value Decomposition - 奇异值分解)</option>
          <option value="Autoencoder" title="自编码器是一种神经网络架构，用于学习数据的紧凑表示（编码），然后尝试重建原始输入。">Autoencoder (自编码器)</option>
        </select>
      </div>

      <div class="form-group">
        <label for="dataset">Dataset:</label>
        <select id="dataset" v-model="selectedDataset" class="form-control">
          <option value="iris" title="鸢尾花数据集是一个著名的分类数据集，包含150个样本，分为3个类别，每个类别50个样本。">Iris (鸢尾花数据集)</option>
          <option value="digits" title="手写数字数据集包含了1797个8x8的灰度图像，每个图像代表一个手写的数字（0-9）。">Digits (手写数字数据集)</option>
          <option value="wine" title="葡萄酒数据集包括了来自意大利同一地区但不同培养种类的三种葡萄酒的化学分析结果。">Wine (葡萄酒数据集)</option>
        </select>
      </div>

      <button type="button" class="btn btn-primary" style="margin-right: 1rem;" @click="toggleShowData">{{ showDataTable ? 'Hide Data' : 'Show Data' }}</button>
     <!-- 应用降维按钮 -->
      <button type="button" class="btn btn-success" :class="{ active: isDimReductionVisible }" style="margin-left: 1rem;" @click="toggleDimReduction">
        {{ isDimReductionVisible ? 'Hide Dimensionality Reduction' : 'Apply Dimensionality Reduction' }}
      </button>
    </form>

    <div v-if="showDataTable" class="mb-4">
      <h3>Data Table</h3>
      <table class="table table-striped">
        <thead>
          <tr>
            <th scope="col">#</th>
            <th scope="col" v-for="(feature, index) in datasetInfo.feature_names" :key="index">{{ feature }}</th>
            <th scope="col">Target</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, rowIndex) in datasetInfo.data" :key="rowIndex">
            <th scope="row">{{ rowIndex + 1 }}</th>
            <td v-for="(value, colIndex) in row" :key="colIndex">{{ value }}</td>
            <td>{{ datasetInfo.targets[rowIndex] }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 降维后数据表格 -->
    <div v-if="isDimReductionVisible && reductionResult && reductionResult.data" class="mb-4">
      <h3>Reduced Data Table</h3>
      <table class="table table-striped">
        <thead>
          <tr>
            <th scope="col">#</th>
            <th scope="col" v-for="(dimention, index) in reductionResult.dimentions" :key="index">{{ dimention }}</th>
            <th scope="col">Target</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, rowIndex) in reductionResult.data" :key="rowIndex">
            <th scope="row">{{ rowIndex + 1 }}</th>
            <td v-for="(value, colIndex) in row" :key="colIndex">{{ value }}</td>
            <td>{{ reductionResult.targets[rowIndex] }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="isDimReductionVisible && reductionResult && reductionResult.data" class="chart-container">
      <h3>Visualization</h3>
      <ChartComponent :chartData="chartData" :options="chartOptions" />
    </div>

    <pre>{{ result }}</pre>
  </div>
</template>

<script>
import axios from 'axios';
import ChartComponent from './ChartComponent.vue';
import { toRaw } from 'vue';

export default {
  components: {
    ChartComponent
  },
  data() {
    return {
      selectedAlgorithm: 'PCA',
      selectedDataset: 'iris',
      datasetInfo: {
        feature_names: [],
        target_names: [],
        data: [],
        targets: []
      },
      showDataTable: false,
      isDimReductionVisible: false, // 新增：用于追踪降维结果是否显示
      reductionResult: null,
      chartData: {},
      chartOptions: {
        responsive: true,
        maintainAspectRatio: false,
        type: 'scatter',
        plugins: {
          legend: {
            display: true
          }
        },
        scales: {
          x: {
            title: {
              display: true,
              text: 'Dimention 1'
            }
          },
          y: {
            title: {
              display: true,
              text: 'Dimention 2'
            }
          }
        }
      },
      result: null,
    };
  },
  //watch: {
    //selectedDataset(newVal, oldVal) {
      //if (this.showDataTable) {
       // this.showData();
     // }
    //}
 // },
  methods: {
    async toggleShowData() {
      this.showDataTable = !this.showDataTable;
      if (this.showDataTable) {
        await this.showData();
      } else {
        this.datasetInfo = {
          feature_names: [],
          target_names:[],
          data: [],
          targets:[]
        };
      }
    },
    async showData() {
      try {
        const response = await axios.post('http://127.0.0.1:5000/api/show-data', {
          dataset: this.selectedDataset.toLowerCase(),
        });
        this.datasetInfo = response.data;
      } catch (error) {
        console.error(error);
        this.datasetInfo = {
          feature_names: [],
          target_names: [],
          data: [],
          targets: []
        };
      }
    },
    async toggleDimReduction() {
      this.isDimReductionVisible = !this.isDimReductionVisible;

      if (this.isDimReductionVisible) {
        await this.applyDimentionalityReduction();
      } else {
        this.reductionResult = null;
        this.chartData = {};
      }
    },
    async applyDimentionalityReduction() {
      try {
        const response = await axios.post('http://127.0.0.1:5000/api/dimention-reduction', {
          algorithm: this.selectedAlgorithm,
          dataset: this.selectedDataset.toLowerCase(),
          parameters: {},
        });
        this.reductionResult = response.data;

        // Prepare data for chart
        if (!this.reductionResult || !this.reductionResult.data) {
          throw new Error("Invalid response structure");
        }

        // 使用 toRaw 解包数据以避免潜在的 Proxy 兼容性问题
        const rawData = toRaw(this.reductionResult.data);
        const rawTargets = toRaw(this.reductionResult.targets);
        const targetNames = toRaw(this.reductionResult.target_names);

        // 构建图表数据集
        const datasets = targetNames.map((targetName, index) => {
            // 将目标名称映射到目标索引
            const targetIndex = index;

            // 获取属于当前类别的所有数据点
            const dataPoints = rawData.filter((_, dataIndex) => rawTargets[dataIndex] === targetIndex)
                                      .map(row => ({ x: row[0], y: row[1] }));

            return {
                label: targetName,
                data: dataPoints,
                fill: false,
                borderColor: this.getRandomColor(),
                tension: 0.1
            };
        });

        // 设置图表数据
        this.chartData = {
            datasets: datasets
        };

        console.log('Reduced Data:', this.reductionResult.data);

      } catch (error) {
        console.error(error);
        this.reductionResult = null;
        this.result = error.response ? error.response.data : 'An error occurred';
      }
    },
    getRandomColor() {
      const letters = '0123456789ABCDEF';
      let color = '#';
      for (let i = 0; i < 6; i++) {
        color += letters[Math.floor(Math.random() * 16)];
      }
      return color;
    }
  },
};
</script>

<style scoped>
/* Add your styles here */
.container {
  max-width: 80%;
}

.form-group {
  margin-bottom: 1rem;
}

.btn {
  margin-top: 1rem;
}

.btn.active {
  background-color: #28a745;
  border-color: #28a745;
}

.btn.active:hover {
  background-color: darken(#28a745, 10%);
  border-color: darken(#28a745, 10%);
}

.chart-container {
  width: 100%;
  max-width: 1200px; /* 你可以根据需要调整最大宽度 */
  margin: 0 auto; /* 居中对齐 */
  padding: 20px; /* 可选：添加一些内边距 */
}

/* 如果需要的话，也可以直接为 ChartComponent 添加样式 */
.ChartComponent {
  width: 100%;
  height: auto;
  min-height: 500px; /* 或者你想要的任何最小高度 */
}
</style>



