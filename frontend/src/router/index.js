import Vue from 'vue';
import Router from 'vue-router';
import Home from '@/components/Home.vue'; // 新的统一页面

Vue.use(Router);

export default new Router({
  mode: 'history',
  routes: [
    {
      path: '/',
      name: 'Home',
      component: Home
    },
    // 其他路由...
  ]
});