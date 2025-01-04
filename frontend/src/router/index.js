import { createRouter, createWebHistory } from 'vue-router';
import Home from '../views/Home.vue'; // 使用相对路径
import FileUploadPage from '../views/FileUploadPage.vue'; // 使用相对路径
import SignalGeneratorPage from '../views/SignalGeneratorPage.vue'; // 使用相对路径
import SignalAnalysisPage from '../views/SignalAnalysisPage.vue';

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/upload',
    name: 'FileUploadPage',
    component: FileUploadPage,
    meta: { keepAlive: true }, // 添加这条属性以启用缓存
  },
  {
    path: '/generator',
    name: 'SignalGeneratorPage',
    component: SignalGeneratorPage,
    meta: { keepAlive: true }, // 添加这条属性以启用缓存
  },
  {
    path: '/analysis',
    name: 'SignalAnalysisPage',
    component: SignalAnalysisPage,
    meta: { keepAlive: true }, // 添加这条属性以启用缓存
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;