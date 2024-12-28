<template>
  <div class="home">
    <el-container>
      <el-header>
        <h1>RemoteBuilder</h1>
      </el-header>
      <el-main>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-card>
              <template #header>
                <div class="card-header">
                  <span>服务器状态</span>
                  <el-button type="primary" @click="refreshServers">刷新</el-button>
                </div>
              </template>
              <el-table :data="servers" style="width: 100%">
                <el-table-column prop="name" label="名称" />
                <el-table-column prop="status" label="状态" />
                <el-table-column label="操作">
                  <template #default="scope">
                    <el-button type="primary" size="small" @click="connectServer(scope.row)">连接</el-button>
                    <el-button type="danger" size="small" @click="disconnectServer(scope.row)">断开</el-button>
                  </template>
                </el-table-column>
              </el-table>
            </el-card>
          </el-col>
          <el-col :span="12">
            <el-card>
              <template #header>
                <div class="card-header">
                  <span>任务列表</span>
                  <el-button type="primary" @click="refreshTasks">刷新</el-button>
                </div>
              </template>
              <el-table :data="tasks" style="width: 100%">
                <el-table-column prop="name" label="名称" />
                <el-table-column prop="status" label="状态" />
                <el-table-column prop="progress" label="进度">
                  <template #default="scope">
                    <el-progress :percentage="scope.row.progress" />
                  </template>
                </el-table-column>
              </el-table>
            </el-card>
          </el-col>
        </el-row>
      </el-main>
    </el-container>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import axios from 'axios'

export default {
  name: 'HomeView',
  setup() {
    const servers = ref([])
    const tasks = ref([])

    const refreshServers = async () => {
      try {
        const response = await axios.get('/api/servers')
        servers.value = response.data
      } catch (error) {
        console.error('Failed to fetch servers:', error)
      }
    }

    const refreshTasks = async () => {
      try {
        const response = await axios.get('/api/tasks')
        tasks.value = response.data
      } catch (error) {
        console.error('Failed to fetch tasks:', error)
      }
    }

    const connectServer = async (server) => {
      try {
        await axios.post(`/api/servers/${server.id}/connect`)
        refreshServers()
      } catch (error) {
        console.error('Failed to connect server:', error)
      }
    }

    const disconnectServer = async (server) => {
      try {
        await axios.post(`/api/servers/${server.id}/disconnect`)
        refreshServers()
      } catch (error) {
        console.error('Failed to disconnect server:', error)
      }
    }

    onMounted(() => {
      refreshServers()
      refreshTasks()
    })

    return {
      servers,
      tasks,
      refreshServers,
      refreshTasks,
      connectServer,
      disconnectServer
    }
  }
}
</script>

<style scoped>
.home {
  height: 100vh;
}
.el-header {
  background-color: #409EFF;
  color: white;
  line-height: 60px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style> 