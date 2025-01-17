<template>
  <div id="app" class="container">
    <!-- 页签导航 -->
    <div class="tabs">
      <router-link to="/" exact active-class="active">主页</router-link>
      <router-link to="/upload" active-class="active">文件上传</router-link>
      <router-link to="/generator" active-class="active">信号发生器</router-link>
      <router-link to="/analysis" active-class="active">信号分析</router-link>
      <router-link to="/dimenreduct" active-class="active">降维展示</router-link>
    </div>

    <!-- 主要内容区域 -->
   <router-view v-slot="{ Component, route }">
      <keep-alive v-if="route.meta.keepAlive">
        <component :is="Component" />
      </keep-alive>
      <component v-else :is="Component" />
    </router-view>


  </div>
</template>

<script>
export default {
  name: 'App',
};
</script>

<style scoped>
.container {
  display: flex;
  flex-direction: column;
}

.tabs {
  display: flex;
  background-color: #f4f4f4;
  padding: 10px;
}

.tabs a {
  margin: 5px;
  padding: 10px 20px;
  text-decoration: none;
  color: #333;
  border-radius: 4px;
}

.tabs a.active {
  background-color: #e9e9e9;
  font-weight: bold;
}

.content {
  padding: 20px;
}
</style>