<template>
  <div class="chart-container" :style="{ height: height + 'px' }">
    <div v-if="loading" class="flex items-center justify-center h-full">
      <div class="text-gray-500">Loading chart data...</div>
    </div>
    <div v-else-if="error" class="flex items-center justify-center h-full">
      <div class="text-red-500">{{ error }}</div>
    </div>
    <div v-else>
      <VueApexCharts
        width="100%"
        :type="type"
        :height="height"
        :options="chartOptions"
        :series="series"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import VueApexCharts from 'vue3-apexcharts'

const props = defineProps({
  height: {
    type: Number,
    default: 350
  },
  type: {
    type: String,
    default: 'donut'
  },
  data: {
    type: Object,
    required: true
  }
})

const loading = ref(true)
const error = ref(null)
const series = ref([])

const chartOptions = ref({
  chart: {
    type: 'donut'
  },
  colors: ['#4F46E5', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6'],
  labels: ['Active', 'Expiring soon', 'Expired', 'Renewed'],
  dataLabels: {
    enabled: true,
    formatter: function(_, opts) {
      const count = opts.w.globals.series[opts.seriesIndex];
      const total = opts.w.globals.seriesTotals.reduce((a, b) => a + b, 0);
      const percentage = ((count / total) * 100).toFixed(1);

      return `${opts.w.config.labels[opts.seriesIndex]}: ${count} (${percentage}%)`;
    }
  },
  plotOptions: {
    pie: {
      donut: {
        size: '70%',
        labels: {
          show: true,
          total: {
            show: true,
            label: 'Total Contracts',
            formatter: function(w) {
              return w.globals.seriesTotals.reduce((a, b) => a + b, 0)
            }
          },
          value: {
            formatter: function(val) {
              return val.toFixed(0)
            }
          }
        }
      }
    }
  },
  legend: {
    position: 'bottom',
    formatter: function(seriesName, opts) {
      return [seriesName, ' - ', opts.w.globals.series[opts.seriesIndex]]
    }
  },
  tooltip: {
    y: {
      formatter: function(value) {
        return value.toFixed(0) + ' contracts'
      }
    }
  }
})

const updateChart = () => {
  try {
    loading.value = true
    error.value = null

    if (!props.data) {
      throw new Error('Invalid data format')
    }

    const total = props.data.total_contracts || 0
    const statusData = [
      {
        label: 'Active',
        count: props.data.active_contracts || 0,
        color: '#10B981'
      },
      {
        label: 'Expiring soon (Within two months)',
        count: props.data.expiring_soon || 0,
        color: '#F59E0B'
      },
      {
        label: 'Expired',
        count: props.data.expired_contracts || 0,
        color: '#EF4444'
      },
      {
        label: 'Renewed',
        count: props.data.renewed_contracts || 0,
        color: '#8B5CF6'
      }
    ]

    // Calculate actual counts instead of percentages
    series.value = statusData.map(item => item.count)

    chartOptions.value = {
      ...chartOptions.value,
      labels: statusData.map(item => item.label),
      colors: statusData.map(item => item.color),
      plotOptions: {
        ...chartOptions.value.plotOptions,
        pie: {
          ...chartOptions.value.plotOptions.pie,
          donut: {
            ...chartOptions.value.plotOptions.pie.donut,
            labels: {
              ...chartOptions.value.plotOptions.pie.donut.labels,
              total: {
                show: true,
                label: 'Total Contracts',
                formatter: function() {
                  return total
                }
              }
            }
          }
        }
      }
    }
  } catch (err) {
    error.value = 'Error loading chart data'
    console.error('Chart error:', err)
    series.value = [0, 0, 0, 0]
    chartOptions.value = {
      ...chartOptions.value,
      labels: ['Active', 'Expiring Soon', 'Expired', 'Renewed']
    }
  } finally {
    loading.value = false
  }
}

watch(() => props.data, updateChart, { deep: true })

onMounted(() => {
  updateChart()
})
</script>

<style scoped>
.chart-container {
  width: 100%;
  min-height: 350px;
}
</style> 