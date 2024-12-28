<template>
  <div class="dashboard">
    <!-- 概览卡片 -->
    <el-row :gutter="20">
      <el-col :span="6">
        <div class="card">
          <div class="overview-item">
            <div class="overview-icon">
              <el-icon><Monitor /></el-icon>
            </div>
            <div class="overview-info">
              <div class="overview-title">服务器总数</div>
              <div class="overview-value">{{ stats.totalServers }}</div>
            </div>
          </div>
        </div>
      </el-col>
      
      <el-col :span="6">
        <div class="card">
          <div class="overview-item">
            <div class="overview-icon">
              <el-icon><Connection /></el-icon>
            </div>
            <div class="overview-info">
              <div class="overview-title">活动服务器</div>
              <div class="overview-value">{{ stats.activeServers }}</div>
            </div>
          </div>
        </div>
      </el-col>
      
      <el-col :span="6">
        <div class="card">
          <div class="overview-item">
            <div class="overview-icon">
              <el-icon><List /></el-icon>
            </div>
            <div class="overview-info">
              <div class="overview-title">任务总数</div>
              <div class="overview-value">{{ stats.totalTasks }}</div>
            </div>
          </div>
        </div>
      </el-col>
      
      <el-col :span="6">
        <div class="card">
          <div class="overview-item">
            <div class="overview-icon">
              <el-icon><Warning /></el-icon>
            </div>
            <div class="overview-info">
              <div class="overview-title">活动告警</div>
              <div class="overview-value">{{ stats.activeAlerts }}</div>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 系统资源监控 -->
    <div class="card">
      <div class="card-header">
        <div class="card-title">系统资源监控</div>
        <el-radio-group v-model="timeRange" size="small">
          <el-radio-button label="1h">1小时</el-radio-button>
          <el-radio-button label="6h">6小时</el-radio-button>
          <el-radio-button label="24h">24小时</el-radio-button>
        </el-radio-group>
      </div>
      <div class="chart-container">
        <v-chart :option="systemResourceOption" autoresize />
      </div>
    </div>

    <!-- 任务执行统计 -->
    <el-row :gutter="20">
      <el-col :span="12">
        <div class="card">
          <div class="card-header">
            <div class="card-title">任务状态分布</div>
          </div>
          <div class="chart-container">
            <v-chart :option="taskStatusOption" autoresize />
          </div>
        </div>
      </el-col>
      
      <el-col :span="12">
        <div class="card">
          <div class="card-header">
            <div class="card-title">任务执行趋势</div>
          </div>
          <div class="chart-container">
            <v-chart :option="taskTrendOption" autoresize />
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 最新告警 -->
    <div class="card">
      <div class="card-header">
        <div class="card-title">最新告警</div>
        <el-button type="primary" link @click="viewAllAlerts">
          查看全部
        </el-button>
      </div>
      <el-table :data="latestAlerts" style="width: 100%">
        <el-table-column prop="timestamp" label="时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.timestamp) }}
          </template>
        </el-table-column>
        <el-table-column prop="level" label="级别" width="100">
          <template #default="{ row }">
            <el-tag
              :type="row.level === 'error' ? 'danger' : 'warning'"
              size="small"
            >
              {{ row.level }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="message" label="内容" />
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { Monitor, Connection, List, Warning } from '@element-plus/icons-vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart, PieChart } from 'echarts/charts'
import {
  GridComponent,
  TooltipComponent,
  LegendComponent,
  TitleComponent
} from 'echarts/components'
import VChart from 'vue-echarts'
import axios from 'axios'

// 注册 ECharts 组件
use([
  CanvasRenderer,
  LineChart,
  PieChart,
  GridComponent,
  TooltipComponent,
  LegendComponent,
  TitleComponent
])

const router = useRouter()
const timeRange = ref('1h')
const refreshInterval = ref(null)

// 统计数据
const stats = ref({
  totalServers: 0,
  activeServers: 0,
  totalTasks: 0,
  activeAlerts: 0
})

// 最新告警
const latestAlerts = ref([])

// ���统资源监控图表配置
const systemResourceOption = ref({
  tooltip: {
    trigger: 'axis'
  },
  legend: {
    data: ['CPU使用率', '内存使用率', '磁盘使用率']
  },
  xAxis: {
    type: 'time',
    boundaryGap: false
  },
  yAxis: {
    type: 'value',
    min: 0,
    max: 100,
    axisLabel: {
      formatter: '{value}%'
    }
  },
  series: [
    {
      name: 'CPU使用率',
      type: 'line',
      smooth: true,
      data: []
    },
    {
      name: '内存使用率',
      type: 'line',
      smooth: true,
      data: []
    },
    {
      name: '磁盘使用率',
      type: 'line',
      smooth: true,
      data: []
    }
  ]
})

// 任务状态分布图表配置
const taskStatusOption = ref({
  tooltip: {
    trigger: 'item'
  },
  legend: {
    orient: 'vertical',
    left: 'left'
  },
  series: [
    {
      type: 'pie',
      radius: '50%',
      data: [],
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowOffsetX: 0,
          shadowColor: 'rgba(0, 0, 0, 0.5)'
        }
      }
    }
  ]
})

// 任务执行趋势图表配置
const taskTrendOption = ref({
  tooltip: {
    trigger: 'axis'
  },
  legend: {
    data: ['创建任务数', '完成任务数']
  },
  xAxis: {
    type: 'time',
    boundaryGap: false
  },
  yAxis: {
    type: 'value'
  },
  series: [
    {
      name: '创建任务数',
      type: 'line',
      smooth: true,
      data: []
    },
    {
      name: '完成任务数',
      type: 'line',
      smooth: true,
      data: []
    }
  ]
})

// 格式化时间
const formatTime = (timestamp) => {
  return new Date(timestamp).toLocaleString()
}

// 获取统计数据
const fetchStats = async () => {
  try {
    const [serversRes, tasksRes, alertsRes] = await Promise.all([
      axios.get('/api/servers/stats'),
      axios.get('/api/tasks/queue'),
      axios.get('/api/monitor/alerts/active')
    ])
    
    stats.value = {
      totalServers: serversRes.data.data.total || 0,
      activeServers: serversRes.data.data.active || 0,
      totalTasks: tasksRes.data.data.total || 0,
      activeAlerts: alertsRes.data.data.length || 0
    }
  } catch (error) {
    console.error('Failed to fetch stats:', error)
  }
}

// 获取系统资源监控数据
const fetchSystemMetrics = async () => {
  try {
    const res = await axios.get('/api/monitor/metrics/system')
    const metrics = res.data.data
    
    // 更新图表数据
    systemResourceOption.value.series[0].data = metrics
      .filter(m => m.name === 'system_cpu_usage')
      .map(m => [m.timestamp, m.value])
      
    systemResourceOption.value.series[1].data = metrics
      .filter(m => m.name === 'system_memory_usage')
      .map(m => [m.timestamp, m.value])
      
    systemResourceOption.value.series[2].data = metrics
      .filter(m => m.name === 'system_disk_usage')
      .map(m => [m.timestamp, m.value])
  } catch (error) {
    console.error('Failed to fetch system metrics:', error)
  }
}

// 获取任务统计数据
const fetchTaskMetrics = async () => {
  try {
    const res = await axios.get('/api/monitor/metrics/tasks')
    const metrics = res.data.data
    
    // 更新任务状态分布
    const statusMetrics = metrics.filter(m => m.name === 'tasks_by_status')
    taskStatusOption.value.series[0].data = statusMetrics.map(m => ({
      name: m.labels.status,
      value: m.value
    }))
    
    // 更新任务执行趋势
    const createdTasks = metrics
      .filter(m => m.name === 'total_tasks')
      .map(m => [m.timestamp, m.value])
      
    const completedTasks = metrics
      .filter(m => m.name === 'task_completion_rate')
      .map(m => [m.timestamp, m.value])
      
    taskTrendOption.value.series[0].data = createdTasks
    taskTrendOption.value.series[1].data = completedTasks
  } catch (error) {
    console.error('Failed to fetch task metrics:', error)
  }
}

// 获取最新告警
const fetchLatestAlerts = async () => {
  try {
    const res = await axios.get('/api/monitor/alerts/active')
    latestAlerts.value = res.data.data.slice(0, 5)
  } catch (error) {
    console.error('Failed to fetch alerts:', error)
  }
}

// 查看所有告警
const viewAllAlerts = () => {
  router.push('/alerts')
}

// 定时刷新数据
const startRefresh = () => {
  fetchStats()
  fetchSystemMetrics()
  fetchTaskMetrics()
  fetchLatestAlerts()
  
  refreshInterval.value = setInterval(() => {
    fetchStats()
    fetchSystemMetrics()
    fetchTaskMetrics()
    fetchLatestAlerts()
  }, 30000) // 每30秒刷新一次
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
.dashboard {
  padding: 20px;
}

.overview-item {
  display: flex;
  align-items: center;
}

.overview-icon {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  background-color: #ecf5ff;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 12px;
}

.overview-icon .el-icon {
  font-size: 24px;
  color: #409eff;
}

.overview-info {
  flex: 1;
}

.overview-title {
  font-size: 14px;
  color: #909399;
  margin-bottom: 4px;
}

.overview-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.chart-container {
  height: 300px;
}
</style> 