/* global globalThis */

globalThis.__VUE_PROD_HYDRATION_MISMATCH_DETAILS__ = false;

import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import './assets/style.css'; // 如果有全局样式文件

// 创建 Vue 应用实例并挂载到 DOM
const app = createApp(App);

app.use(router);
// app.use(store); // 如果你使用 Vuex 也需要这行

app.mount('#app');