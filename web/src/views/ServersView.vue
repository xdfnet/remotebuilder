<template>
  <div class="servers">
    <!-- 工具栏 -->
    <div class="toolbar">
      <el-button type="primary" @click="showAddServerDialog">
        <el-icon><Plus /></el-icon>
        添加服务器
      </el-button>
      <el-button @click="refreshServers">
        <el-icon><Refresh /></el-icon>
        刷新
      </el-button>
    </div>

    <!-- 服务器列表 -->
    <div class="card">
      <el-table :data="servers" style="width: 100%">
        <el-table-column prop="name" label="名称" width="180" />
        <el-table-column prop="type" label="类型" width="120" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag
              :type="row.is_active ? 'success' : 'danger'"
              size="small"
            >
              {{ row.is_active ? '在线' : '离线' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="资源使用率">
          <template #default="{ row }">
            <div class="resource-usage">
              <div class="usage-item">
                <span class="usage-label">CPU:</span>
                <el-progress
                  :percentage="row.health?.cpu_usage || 0"
                  :status="getUsageStatus(row.health?.cpu_usage)"
                />
              </div>
              <div class="usage-item">
                <span class="usage-label">内存:</span>
                <el-progress
                  :percentage="row.health?.memory_usage || 0"
                  :status="getUsageStatus(row.health?.memory_usage)"
                />
              </div>
              <div class="usage-item">
                <span class="usage-label">磁盘:</span>
                <el-progress
                  :percentage="row.health?.disk_usage || 0"
                  :status="getUsageStatus(row.health?.disk_usage)"
                />
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="负载" width="120">
          <template #default="{ row }">
            <el-progress
              :percentage="Math.round(row.load * 100)"
              :status="getUsageStatus(row.load * 100)"
            />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="250">
          <template #default="{ row }">
            <div class="table-actions">
              <el-button
                v-if="!row.is_active"
                type="primary"
                size="small"
                @click="connectServer(row.name)"
              >
                连接
              </el-button>
              <el-button
                v-else
                type="warning"
                size="small"
                @click="disconnectServer(row.name)"
              >
                断开
              </el-button>
              <el-button
                type="primary"
                size="small"
                @click="checkServerHealth(row.name)"
              >
                检查健康
              </el-button>
              <el-button
                type="danger"
                size="small"
                @click="confirmRemoveServer(row.name)"
              >
                移除
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 添加服务器对话框 -->
    <el-dialog
      v-model="addServerDialog.visible"
      title="添加服务器"
      width="500px"
    >
      <el-form
        ref="addServerForm"
        :model="addServerDialog.form"
        :rules="addServerDialog.rules"
        label-width="100px"
      >
        <el-form-item label="名称" prop="name">
          <el-input v-model="addServerDialog.form.name" />
        </el-form-item>
        <el-form-item label="类型" prop="type">
          <el-select v-model="addServerDialog.form.type" style="width: 100%">
            <el-option label="Linux" value="linux" />
            <el-option label="Windows" value="windows" />
            <el-option label="macOS" value="macos" />
          </el-select>
        </el-form-item>
        <el-form-item label="主机" prop="host">
          <el-input v-model="addServerDialog.form.config.host" />
        </el-form-item>
        <el-form-item label="端口" prop="port">
          <el-input-number
            v-model="addServerDialog.form.config.port"
            :min="1"
            :max="65535"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="用户名" prop="username">
          <el-input v-model="addServerDialog.form.config.username" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input
            v-model="addServerDialog.form.config.password"
            type="password"
            show-password
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addServerDialog.visible = false">取消</el-button>
        <el-button type="primary" @click="addServer">确定</el-button>
      </template>
    </el-dialog>

    <!-- 健康检查结果对话框 -->
    <el-dialog
      v-model="healthCheckDialog.visible"
      title="健康检查结果"
      width="600px"
    >
      <div v-if="healthCheckDialog.result">
        <div class="health-check-item">
          <span class="health-check-label">CPU使用率:</span>
          <el-progress
            :percentage="healthCheckDialog.result.cpu_usage"
            :status="getUsageStatus(healthCheckDialog.result.cpu_usage)"
          />
        </div>
        <div class="health-check-item">
          <span class="health-check-label">内存使用率:</span>
          <el-progress
            :percentage="healthCheckDialog.result.memory_usage"
            :status="getUsageStatus(healthCheckDialog.result.memory_usage)"
          />
        </div>
        <div class="health-check-item">
          <span class="health-check-label">磁盘使用率:</span>
          <el-progress
            :percentage="healthCheckDialog.result.disk_usage"
            :status="getUsageStatus(healthCheckDialog.result.disk_usage)"
          />
        </div>
        <div v-if="healthCheckDialog.result.errors.length > 0">
          <div class="health-check-errors">
            <h4>错误信息:</h4>
            <ul>
              <li v-for="error in healthCheckDialog.result.errors" :key="error">
                {{ error }}
              </li>
            </ul>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { Plus, Refresh } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'

// 服务器列表
const servers = ref([])

// 添加服务器对话框
const addServerDialog = ref({
  visible: false,
  form: {
    name: '',
    type: '',
    config: {
      host: '',
      port: 22,
      username: '',
      password: ''
    }
  },
  rules: {
    name: [
      { required: true, message: '请输入服务器名称', trigger: 'blur' },
      { min: 2, max: 20, message: '长度在 2 到 20 个字符', trigger: 'blur' }
    ],
    type: [
      { required: true, message: '请选择服务器类型', trigger: 'change' }
    ],
    host: [
      { required: true, message: '请输入主机地址', trigger: 'blur' }
    ],
    port: [
      { required: true, message: '请输入端口号', trigger: 'blur' },
      { type: 'number', message: '端口号必须为数字', trigger: 'blur' }
    ],
    username: [
      { required: true, message: '请输入用户名', trigger: 'blur' }
    ],
    password: [
      { required: true, message: '请输入密码', trigger: 'blur' }
    ]
  }
})

// 健康检查对话框
const healthCheckDialog = ref({
  visible: false,
  result: null
})

// 刷新间隔
const refreshInterval = ref(null)

// 获取服务器列表
const fetchServers = async () => {
  try {
    const res = await axios.get('/api/servers')
    servers.value = res.data.data
  } catch (error) {
    console.error('Failed to fetch servers:', error)
    ElMessage.error('获取服务器列表失败')
  }
}

// 添加服务器
const addServer = async () => {
  try {
    const res = await axios.post('/api/servers', addServerDialog.value.form)
    if (res.data.success) {
      ElMessage.success('添加服务器成功')
      addServerDialog.value.visible = false
      fetchServers()
    } else {
      ElMessage.error(res.data.message || '添加服务器失败')
    }
  } catch (error) {
    console.error('Failed to add server:', error)
    ElMessage.error('添加服务器失败')
  }
}

// 移除服务器
const removeServer = async (name) => {
  try {
    const res = await axios.delete(`/api/servers/${name}`)
    if (res.data.success) {
      ElMessage.success('移除服务器成功')
      fetchServers()
    } else {
      ElMessage.error(res.data.message || '移除服务器失败')
    }
  } catch (error) {
    console.error('Failed to remove server:', error)
    ElMessage.error('移除服务器失败')
  }
}

// 连接服务器
const connectServer = async (name) => {
  try {
    const res = await axios.post(`/api/servers/${name}/connect`)
    if (res.data.success) {
      ElMessage.success('连接服务器成功')
      fetchServers()
    } else {
      ElMessage.error(res.data.message || '连接服务器失败')
    }
  } catch (error) {
    console.error('Failed to connect server:', error)
    ElMessage.error('连接服务器失败')
  }
}

// 断开服务器
const disconnectServer = async (name) => {
  try {
    const res = await axios.post(`/api/servers/${name}/disconnect`)
    if (res.data.success) {
      ElMessage.success('断开服务器成功')
      fetchServers()
    } else {
      ElMessage.error(res.data.message || '断开服务器失败')
    }
  } catch (error) {
    console.error('Failed to disconnect server:', error)
    ElMessage.error('断开服务器失败')
  }
}

// 检查服务器健康状态
const checkServerHealth = async (name) => {
  try {
    const res = await axios.get(`/api/servers/${name}/health`)
    if (res.data.success) {
      healthCheckDialog.value.result = res.data.data
      healthCheckDialog.value.visible = true
    } else {
      ElMessage.error(res.data.message || '检查服务器健康状态失败')
    }
  } catch (error) {
    console.error('Failed to check server health:', error)
    ElMessage.error('检查服务器健康状态失败')
  }
}

// 确认移除服务器
const confirmRemoveServer = (name) => {
  ElMessageBox.confirm(
    '确定要移除该服务器吗？此操作不可恢复',
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  )
    .then(() => {
      removeServer(name)
    })
    .catch(() => {})
}

// 显示添加服务器对话框
const showAddServerDialog = () => {
  addServerDialog.value.form = {
    name: '',
    type: '',
    config: {
      host: '',
      port: 22,
      username: '',
      password: ''
    }
  }
  addServerDialog.value.visible = true
}

// 刷新服务器列表
const refreshServers = () => {
  fetchServers()
}

// 获取使用率状态
const getUsageStatus = (value) => {
  if (value >= 90) return 'exception'
  if (value >= 70) return 'warning'
  return 'success'
}

// 定时刷新数据
const startRefresh = () => {
  fetchServers()
  refreshInterval.value = setInterval(fetchServers, 30000) // 每30秒刷新一次
}

onMounted(() => {
  startRefresh()
})

onUnmounted(() => {
  if (refreshInterval.value) {
    clearInterval(refreshInterval.value)
  }
})
</script>

<style scoped>
.servers {
  padding: 20px;
}

.resource-usage {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.usage-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.usage-label {
  width: 50px;
  color: #606266;
}

.health-check-item {
  margin-bottom: 16px;
}

.health-check-label {
  display: inline-block;
  width: 100px;
  color: #606266;
}

.health-check-errors {
  margin-top: 16px;
  padding: 16px;
  background-color: #fef0f0;
  border-radius: 4px;
}

.health-check-errors h4 {
  color: #f56c6c;
  margin-bottom: 8px;
}

.health-check-errors ul {
  margin: 0;
  padding-left: 20px;
}

.health-check-errors li {
  color: #f56c6c;
  line-height: 1.5;
}
</style> 