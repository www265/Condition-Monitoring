/* global globalThis */

globalThis.__VUE_PROD_HYDRATION_MISMATCH_DETAILS__ = false;

import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import './assets/style.css'; // 如果有全局样式文件
import 'bootstrap/dist/css/bootstrap.css';

// 创建 Vue 应用实例
const app = createApp(App);

// 使用路由（如果有的话）
app.use(router);

// 如果你使用 Vuex 或其他插件，也需要在这里注册
// app.use(store);

// 挂载应用到 DOM
app.mount('#app');