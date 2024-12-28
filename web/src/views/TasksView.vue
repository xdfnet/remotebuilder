<template>
  <div class="tasks">
    <!-- 工具栏 -->
    <div class="toolbar">
      <el-button type="primary" @click="showCreateTaskDialog">
        <el-icon><Plus /></el-icon>
        创建任务
      </el-button>
      <el-button @click="refreshTasks">
        <el-icon><Refresh /></el-icon>
        刷新
      </el-button>
    </div>

    <!-- 任务列表 -->
    <div class="card">
      <el-table :data="tasks" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="名称" width="180" />
        <el-table-column prop="server" label="服务器" width="120" />
        <el-table-column prop="type" label="类型" width="120">
          <template #default="{ row }">
            <el-tag size="small">{{ row.type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag
              :type="getStatusType(row.status)"
              size="small"
            >
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="进度" width="200">
          <template #default="{ row }">
            <el-progress
              :percentage="row.progress"
              :status="getProgressStatus(row.status)"
            />
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <div class="table-actions">
              <el-button
                v-if="row.status === 'pending' || row.status === 'running'"
                type="danger"
                size="small"
                @click="cancelTask(row.id)"
              >
                取消
              </el-button>
              <el-button
                type="primary"
                size="small"
                @click="viewTaskDetails(row)"
              >
                详情
              </el-button>
              <el-button
                v-if="row.status === 'completed'"
                type="success"
                size="small"
                @click="downloadArtifact(row.id)"
              >
                下载
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 创建任务对话框 -->
    <el-dialog
      v-model="createTaskDialog.visible"
      title="创建任务"
      width="600px"
    >
      <el-form
        ref="createTaskForm"
        :model="createTaskDialog.form"
        :rules="createTaskDialog.rules"
        label-width="100px"
      >
        <el-form-item label="名称" prop="name">
          <el-input v-model="createTaskDialog.form.name" />
        </el-form-item>
        <el-form-item label="服务器" prop="server">
          <el-select v-model="createTaskDialog.form.server" style="width: 100%">
            <el-option
              v-for="server in servers"
              :key="server.name"
              :label="server.name"
              :value="server.name"
              :disabled="!server.is_active"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="构建类型" prop="type">
          <el-select v-model="createTaskDialog.form.type" style="width: 100%">
            <el-option label="PyInstaller" value="pyinstaller" />
            <el-option label="cx_Freeze" value="cx_freeze" />
            <el-option label="py2exe" value="py2exe" />
            <el-option label="py2app" value="py2app" />
          </el-select>
        </el-form-item>
        <el-form-item label="入口脚本" prop="entry_script">
          <el-input v-model="createTaskDialog.form.config.entry_script" />
        </el-form-item>
        <el-form-item label="工作目录" prop="workspace">
          <el-input v-model="createTaskDialog.form.config.workspace" />
        </el-form-item>
        <el-form-item label="输出目录" prop="output_dir">
          <el-input v-model="createTaskDialog.form.config.output_dir" />
        </el-form-item>
        <el-form-item label="图标" prop="icon">
          <el-input v-model="createTaskDialog.form.config.icon" />
        </el-form-item>
        <el-form-item label="附加文件">
          <el-input
            v-model="createTaskDialog.form.config.additional_files"
            type="textarea"
            rows="3"
            placeholder="每行一个文件路径"
          />
        </el-form-item>
        <el-form-item label="环境变量">
          <el-input
            v-model="createTaskDialog.form.config.env_vars"
            type="textarea"
            rows="3"
            placeholder="格式: KEY=VALUE, 每行一个"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createTaskDialog.visible = false">取消</el-button>
        <el-button type="primary" @click="createTask">确定</el-button>
      </template>
    </el-dialog>

    <!-- 任务详情对话框 -->
    <el-dialog
      v-model="taskDetailsDialog.visible"
      :title="'任务详情 - ' + (taskDetailsDialog.task?.name || '')"
      width="800px"
    >
      <div v-if="taskDetailsDialog.task">
        <div class="task-info">
          <div class="info-item">
            <span class="info-label">ID:</span>
            <span>{{ taskDetailsDialog.task.id }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">名称:</span>
            <span>{{ taskDetailsDialog.task.name }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">服务器:</span>
            <span>{{ taskDetailsDialog.task.server }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">类型:</span>
            <span>{{ taskDetailsDialog.task.type }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">状态:</span>
            <el-tag
              :type="getStatusType(taskDetailsDialog.task.status)"
              size="small"
            >
              {{ taskDetailsDialog.task.status }}
            </el-tag>
          </div>
          <div class="info-item">
            <span class="info-label">进度:</span>
            <el-progress
              :percentage="taskDetailsDialog.task.progress"
              :status="getProgressStatus(taskDetailsDialog.task.status)"
            />
          </div>
          <div class="info-item">
            <span class="info-label">创建时间:</span>
            <span>{{ formatTime(taskDetailsDialog.task.created_at) }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">开始时间:</span>
            <span>{{ formatTime(taskDetailsDialog.task.started_at) }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">完成时间:</span>
            <span>{{ formatTime(taskDetailsDialog.task.finished_at) }}</span>
          </div>
        </div>

        <div class="task-config">
          <h4>配置信息</h4>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="入口脚本">
              {{ taskDetailsDialog.task.config.entry_script }}
            </el-descriptions-item>
            <el-descriptions-item label="工作目录">
              {{ taskDetailsDialog.task.config.workspace }}
            </el-descriptions-item>
            <el-descriptions-item label="输出目录">
              {{ taskDetailsDialog.task.config.output_dir }}
            </el-descriptions-item>
            <el-descriptions-item label="图标">
              {{ taskDetailsDialog.task.config.icon }}
            </el-descriptions-item>
            <el-descriptions-item label="附加文件">
              <pre>{{ taskDetailsDialog.task.config.additional_files?.join('\n') }}</pre>
            </el-descriptions-item>
            <el-descriptions-item label="环境变量">
              <pre>{{ formatEnvVars(taskDetailsDialog.task.config.env_vars) }}</pre>
            </el-descriptions-item>
          </el-descriptions>
        </div>

        <div v-if="taskDetailsDialog.task.logs" class="task-logs">
          <h4>任务日志</h4>
          <el-input
            v-model="taskDetailsDialog.task.logs"
            type="textarea"
            rows="10"
            readonly
          />
        </div>

        <div v-if="taskDetailsDialog.task.error" class="task-error">
          <h4>错误信息</h4>
          <pre>{{ taskDetailsDialog.task.error }}</pre>
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

// 任务列表
const tasks = ref([])

// 服务器列表
const servers = ref([])

// 创建任务对话框
const createTaskDialog = ref({
  visible: false,
  form: {
    name: '',
    server: '',
    type: '',
    config: {
      entry_script: '',
      workspace: '',
      output_dir: '',
      icon: '',
      additional_files: '',
      env_vars: ''
    }
  },
  rules: {
    name: [
      { required: true, message: '请输入任务名称', trigger: 'blur' },
      { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
    ],
    server: [
      { required: true, message: '请选择服务器', trigger: 'change' }
    ],
    type: [
      { required: true, message: '请选择构建类型', trigger: 'change' }
    ],
    entry_script: [
      { required: true, message: '请输入入口脚本路径', trigger: 'blur' }
    ],
    workspace: [
      { required: true, message: '请输入工作目录路径', trigger: 'blur' }
    ],
    output_dir: [
      { required: true, message: '请输入输出目录路径', trigger: 'blur' }
    ]
  }
})

// 任务详情���话框
const taskDetailsDialog = ref({
  visible: false,
  task: null
})

// 刷新间隔
const refreshInterval = ref(null)

// 获取任务列表
const fetchTasks = async () => {
  try {
    const res = await axios.get('/api/tasks')
    tasks.value = res.data.data
  } catch (error) {
    console.error('Failed to fetch tasks:', error)
    ElMessage.error('获取任务列表失败')
  }
}

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

// 创建任务
const createTask = async () => {
  try {
    // 处理附加文件和环境变量
    const config = { ...createTaskDialog.value.form.config }
    if (config.additional_files) {
      config.additional_files = config.additional_files
        .split('\n')
        .map(f => f.trim())
        .filter(f => f)
    }
    if (config.env_vars) {
      const envVars = {}
      config.env_vars
        .split('\n')
        .map(line => line.trim())
        .filter(line => line)
        .forEach(line => {
          const [key, value] = line.split('=').map(s => s.trim())
          if (key && value) {
            envVars[key] = value
          }
        })
      config.env_vars = envVars
    }

    const data = {
      ...createTaskDialog.value.form,
      config
    }

    const res = await axios.post('/api/tasks', data)
    if (res.data.success) {
      ElMessage.success('创建任务成功')
      createTaskDialog.value.visible = false
      fetchTasks()
    } else {
      ElMessage.error(res.data.message || '创建任务失败')
    }
  } catch (error) {
    console.error('Failed to create task:', error)
    ElMessage.error('创建任务失败')
  }
}

// 取消任务
const cancelTask = async (id) => {
  try {
    const res = await axios.post(`/api/tasks/${id}/cancel`)
    if (res.data.success) {
      ElMessage.success('取消任务成功')
      fetchTasks()
    } else {
      ElMessage.error(res.data.message || '取消任务失败')
    }
  } catch (error) {
    console.error('Failed to cancel task:', error)
    ElMessage.error('取消任务失败')
  }
}

// 下载构建产物
const downloadArtifact = async (id) => {
  try {
    const res = await axios.get(`/api/tasks/${id}/artifact`, {
      responseType: 'blob'
    })
    const url = window.URL.createObjectURL(new Blob([res.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `task-${id}-artifact.zip`)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  } catch (error) {
    console.error('Failed to download artifact:', error)
    ElMessage.error('下载构建产物失败')
  }
}

// 查看任务详情
const viewTaskDetails = async (task) => {
  try {
    const res = await axios.get(`/api/tasks/${task.id}`)
    if (res.data.success) {
      taskDetailsDialog.value.task = res.data.data
      taskDetailsDialog.value.visible = true
    } else {
      ElMessage.error(res.data.message || '获取任务详情失败')
    }
  } catch (error) {
    console.error('Failed to fetch task details:', error)
    ElMessage.error('获取任务详情失败')
  }
}

// 显示创建任务对话框
const showCreateTaskDialog = () => {
  createTaskDialog.value.form = {
    name: '',
    server: '',
    type: '',
    config: {
      entry_script: '',
      workspace: '',
      output_dir: '',
      icon: '',
      additional_files: '',
      env_vars: ''
    }
  }
  createTaskDialog.value.visible = true
}

// 刷新任务列表
const refreshTasks = () => {
  fetchTasks()
}

// 获取状态类型
const getStatusType = (status) => {
  switch (status) {
    case 'completed':
      return 'success'
    case 'failed':
      return 'danger'
    case 'running':
      return 'primary'
    case 'pending':
      return 'warning'
    case 'cancelled':
      return 'info'
    default:
      return ''
  }
}

// 获取进度状态
const getProgressStatus = (status) => {
  switch (status) {
    case 'completed':
      return 'success'
    case 'failed':
      return 'exception'
    case 'cancelled':
      return 'warning'
    default:
      return ''
  }
}

// 格式化时间
const formatTime = (timestamp) => {
  if (!timestamp) return '-'
  return new Date(timestamp).toLocaleString()
}

// 格式化环境变量
const formatEnvVars = (envVars) => {
  if (!envVars) return ''
  return Object.entries(envVars)
    .map(([key, value]) => `${key}=${value}`)
    .join('\n')
}

// 定时刷新数据
const startRefresh = () => {
  fetchTasks()
  fetchServers()
  refreshInterval.value = setInterval(fetchTasks, 5000) // 每5秒刷新一次
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
.tasks {
  padding: 20px;
}

.task-info {
  margin-bottom: 24px;
}

.info-item {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
}

.info-label {
  width: 100px;
  color: #606266;
}

.task-config {
  margin-bottom: 24px;
}

.task-config h4,
.task-logs h4,
.task-error h4 {
  margin-bottom: 12px;
  color: #303133;
}

.task-logs {
  margin-bottom: 24px;
}

.task-error {
  margin-bottom: 24px;
}

.task-error pre {
  padding: 12px;
  background-color: #fef0f0;
  border-radius: 4px;
  color: #f56c6c;
  margin: 0;
  white-space: pre-wrap;
  word-wrap: break-word;
}

pre {
  margin: 0;
  white-space: pre-wrap;
  word-wrap: break-word;
  font-family: monospace;
}
</style> 