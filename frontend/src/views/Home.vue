<template>
  <div class="HomePage">
    <h1>Welcome to the Condition Monitoring System</h1>
    <p>This is the home page of your application.</p>
    <nav>
      <router-link to="/upload">Go to File Upload</router-link> |
      <router-link to="/generator">Go to Signal Generator</router-link> |
      <router-link to="/analysis">Go to Signal Analysis</router-link>
      <router-link to="/dimenreduct" active-class="active">Go to Dimension Reduction</router-link>
    </nav>
  </div>
</template>

<script>
export default {
  name: 'HomePage', // 更改为多单词形式
  mounted() {
    console.log('HomePage component mounted');
  }
};
</script>

<style scoped>
.HomePage {
  text-align: center;
  margin-top: 100px;
}

nav {
  margin-top: 20px;
}

nav a {
  margin: 0 10px;
  text-decoration: none;
  color: #4CAF50;
}

nav a:hover {
  text-decoration: underline;
}
</style>