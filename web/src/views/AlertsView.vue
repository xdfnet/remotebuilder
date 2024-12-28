<template>
  <div class="alerts">
    <!-- 工具栏 -->
    <div class="toolbar">
      <div class="toolbar-left">
        <el-radio-group v-model="filter.status" size="small">
          <el-radio-button label="active">活动告警</el-radio-button>
          <el-radio-button label="resolved">已解决</el-radio-button>
          <el-radio-button label="all">全部</el-radio-button>
        </el-radio-group>
      </div>
      <div class="toolbar-right">
        <el-button @click="refreshAlerts">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
    </div>

    <!-- 告警列表 -->
    <div class="card">
      <el-table :data="filteredAlerts" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column label="级别" width="100">
          <template #default="{ row }">
            <el-tag
              :type="getAlertLevelType(row.level)"
              size="small"
            >
              {{ row.level }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag
              :type="row.resolved ? 'success' : 'danger'"
              size="small"
            >
              {{ row.resolved ? '已解决' : '未解决' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="source" label="来源" width="120" />
        <el-table-column prop="message" label="内容" />
        <el-table-column prop="created_at" label="发生时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="resolved_at" label="解决时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.resolved_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <div class="table-actions">
              <el-button
                v-if="!row.resolved"
                type="primary"
                size="small"
                @click="resolveAlert(row.id)"
              >
                标记解决
              </el-button>
              <el-button
                type="primary"
                link
                size="small"
                @click="viewAlertDetails(row)"
              >
                详情
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 告警详情对话框 -->
    <el-dialog
      v-model="alertDetailsDialog.visible"
      title="告警详情"
      width="600px"
    >
      <div v-if="alertDetailsDialog.alert">
        <div class="alert-info">
          <div class="info-item">
            <span class="info-label">ID:</span>
            <span>{{ alertDetailsDialog.alert.id }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">级别:</span>
            <el-tag
              :type="getAlertLevelType(alertDetailsDialog.alert.level)"
              size="small"
            >
              {{ alertDetailsDialog.alert.level }}
            </el-tag>
          </div>
          <div class="info-item">
            <span class="info-label">状态:</span>
            <el-tag
              :type="alertDetailsDialog.alert.resolved ? 'success' : 'danger'"
              size="small"
            >
              {{ alertDetailsDialog.alert.resolved ? '已解决' : '未解决' }}
            </el-tag>
          </div>
          <div class="info-item">
            <span class="info-label">来源:</span>
            <span>{{ alertDetailsDialog.alert.source }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">发生时间:</span>
            <span>{{ formatTime(alertDetailsDialog.alert.created_at) }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">解决时间:</span>
            <span>{{ formatTime(alertDetailsDialog.alert.resolved_at) }}</span>
          </div>
        </div>

        <div class="alert-message">
          <h4>告警内容</h4>
          <p>{{ alertDetailsDialog.alert.message }}</p>
        </div>

        <div v-if="alertDetailsDialog.alert.details" class="alert-details">
          <h4>详细信息</h4>
          <pre>{{ JSON.stringify(alertDetailsDialog.alert.details, null, 2) }}</pre>
        </div>

        <div v-if="alertDetailsDialog.alert.resolution" class="alert-resolution">
          <h4>解决方案</h4>
          <p>{{ alertDetailsDialog.alert.resolution }}</p>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { Refresh } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

// 告警列表
const alerts = ref([])

// 过滤条件
const filter = ref({
  status: 'active'
})

// 告警详情对话框
const alertDetailsDialog = ref({
  visible: false,
  alert: null
})

// 刷新间隔
const refreshInterval = ref(null)

// 过滤后的告警列表
const filteredAlerts = computed(() => {
  switch (filter.value.status) {
    case 'active':
      return alerts.value.filter(alert => !alert.resolved)
    case 'resolved':
      return alerts.value.filter(alert => alert.resolved)
    default:
      return alerts.value
  }
})

// 获取告警列表
const fetchAlerts = async () => {
  try {
    const res = await axios.get('/api/monitor/alerts')
    alerts.value = res.data.data
  } catch (error) {
    console.error('Failed to fetch alerts:', error)
    ElMessage.error('获取告警列表失败')
  }
}

// 标记告警已解决
const resolveAlert = async (id) => {
  try {
    const res = await axios.post(`/api/monitor/alerts/${id}/resolve`)
    if (res.data.success) {
      ElMessage.success('标记告警已解决')
      fetchAlerts()
    } else {
      ElMessage.error(res.data.message || '标记告警已解决失败')
    }
  } catch (error) {
    console.error('Failed to resolve alert:', error)
    ElMessage.error('标记告警已解决失败')
  }
}

// 查看告警详情
const viewAlertDetails = async (alert) => {
  try {
    const res = await axios.get(`/api/monitor/alerts/${alert.id}`)
    if (res.data.success) {
      alertDetailsDialog.value.alert = res.data.data
      alertDetailsDialog.value.visible = true
    } else {
      ElMessage.error(res.data.message || '获取告警详情失败')
    }
  } catch (error) {
    console.error('Failed to fetch alert details:', error)
    ElMessage.error('获取告警详情失败')
  }
}

// 刷新告警列表
const refreshAlerts = () => {
  fetchAlerts()
}

// 获取告警级别类型
const getAlertLevelType = (level) => {
  switch (level) {
    case 'critical':
      return 'danger'
    case 'error':
      return 'danger'
    case 'warning':
      return 'warning'
    case 'info':
      return 'info'
    default:
      return ''
  }
}

// 格式化时间
const formatTime = (timestamp) => {
  if (!timestamp) return '-'
  return new Date(timestamp).toLocaleString()
}

// 定时刷新数据
const startRefresh = () => {
  fetchAlerts()
  refreshInterval.value = setInterval(fetchAlerts, 10000) // 每10秒刷新一次
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
.alerts {
  padding: 20px;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.alert-info {
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

.alert-message,
.alert-details,
.alert-resolution {
  margin-bottom: 24px;
}

.alert-message h4,
.alert-details h4,
.alert-resolution h4 {
  margin-bottom: 12px;
  color: #303133;
}

.alert-details pre {
  padding: 12px;
  background-color: #f5f7fa;
  border-radius: 4px;
  margin: 0;
  white-space: pre-wrap;
  word-wrap: break-word;
  font-family: monospace;
}
</style> 