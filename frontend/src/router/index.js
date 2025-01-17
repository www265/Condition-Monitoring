import { createRouter, createWebHistory } from 'vue-router';
import Home from '../views/Home.vue'; // 使用相对路径
import FileUpload from '../components/FileUpload.vue'; // 使用相对路径
import SignalGenerator from '../components/SignalGenerator.vue'; // 使用相对路径
import SignalAnalysis from '../components/SignalAnalysis.vue';
import DimentionReduction from '../components/DimentionReduction.vue';

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/upload',
    name: 'FileUpload',
    component: FileUpload,
    meta: { keepAlive: true }, // 添加这条属性以启用缓存
  },
  {
    path: '/generator',
    name: 'SignalGenerator',
    component: SignalGenerator,
    meta: { keepAlive: true }, // 添加这条属性以启用缓存
  },
  {
    path: '/analysis',
    name: 'SignalAnalysis',
    component: SignalAnalysis,
    meta: { keepAlive: true }, // 添加这条属性以启用缓存
  },
  {
    path: '/dimenreduct',
    name: 'DimentionReduction',
    component: DimentionReduction,
    meta: { keepAlive: true }, // 添加这条属性以启用缓存
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;