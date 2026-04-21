<template>
  <el-config-provider :locale="zhCn">
    <router-view />
  </el-config-provider>
</template>

<script setup>
import zhCn from 'element-plus/es/locale/lang/zh-cn'
</script>

<style>
* { box-sizing: border-box; }
body {
  margin: 0;
  background: #f0eeff;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Helvetica Neue', sans-serif;
}
/* 全局卡片阴影 */
.el-card {
  border-radius: 12px !important;
  box-shadow: 0 2px 12px rgba(118, 75, 162, 0.08) !important;
  border: 1px solid #e8e0ff !important;
}
/* Element Plus 主色调覆盖为紫色 */
:root {
  --el-color-primary: #764ba2;
  --el-color-primary-light-3: #9b72c3;
  --el-color-primary-light-5: #b899d4;
  --el-color-primary-light-7: #d4bfe8;
  --el-color-primary-light-8: #e4d6f2;
  --el-color-primary-light-9: #f2ebf9;
  --el-color-primary-dark-2: #5e3a82;
}
</style>
