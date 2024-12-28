<template>
  <el-container class="app-container">
    <el-aside width="200px">
      <el-menu
        router
        :default-active="$route.path"
        class="el-menu-vertical"
      >
        <el-menu-item index="/">
          <el-icon><Monitor /></el-icon>
          <span>服务器管理</span>
        </el-menu-item>
        <el-menu-item index="/tasks">
          <el-icon><List /></el-icon>
          <span>任务管理</span>
        </el-menu-item>
        <el-menu-item index="/alerts">
          <el-icon><Warning /></el-icon>
          <span>告警中心</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script>
import { Monitor, List, Warning } from '@element-plus/icons-vue'

export default {
  name: 'App',
  components: {
    Monitor,
    List,
    Warning
  }
}
</script>

<style>
.app-container {
  height: 100vh;
}
.el-aside {
  background-color: #304156;
}
.el-menu {
  border-right: none;
}
.el-menu-vertical {
  height: 100%;
}
</style> 