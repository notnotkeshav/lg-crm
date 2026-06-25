<template>
  <div class="chart-container" :style="{ height: height + 'px' }">
    <div v-if="!hasValidData" class="flex items-center justify-center h-full">
      <div class="text-gray-500">No chart data available</div>
    </div>
    <VueApexCharts
      v-else
      :key="chartKey"
      width="100%"
      :type="type"
      :height="height"
      :options="chartOptions"
      :series="series"
    />
  </div>
</template>

<script setup>
import { computed, watch, ref } from 'vue'
import VueApexCharts from 'vue3-apexcharts'

const props = defineProps({
  height: { type: Number, default: 350 },
  type: { type: String, default: 'bar' },
  data: { type: Object, required: true }
})

const chartKey = ref(0) // Force re-render

const formatCurrency = (value) => {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0
  }).format(value || 0)
}

// Deep unwrap for nested proxies
const deepUnwrap = (obj) => {
  if (!obj) return obj
  if (Array.isArray(obj)) {
    return obj.map(item => deepUnwrap(item))
  }
  if (typeof obj === 'object' && obj !== null) {
    if (obj.__v_isRef) return deepUnwrap(obj.value)
    const unwrapped = {}
    for (const key in obj) {
      unwrapped[key] = deepUnwrap(obj[key])
    }
    return unwrapped
  }
  return obj
}

const hasValidData = computed(() => {
  const rawData = deepUnwrap(props.data)
  const trendData = rawData?.trend_data
  const isValid = Array.isArray(trendData) && trendData.length > 0
  console.log('📊 QuotationAnalysisChart hasValidData:', isValid, trendData)
  return isValid
})

const series = computed(() => {
  const rawData = deepUnwrap(props.data)
  const trendData = rawData?.trend_data
  
  if (!Array.isArray(trendData) || trendData.length === 0) {
    console.warn('⚠️ QuotationAnalysisChart: No valid trend_data')
    return []
  }
  
  const openValues = []
  const approvedValues = []
  const wonValues = []

  trendData.forEach((month) => {
    openValues.push(Number(month?.open_value) || 0)
    approvedValues.push(Number(month?.approved_value) || 0)
    wonValues.push(Number(month?.won_value) || 0)
  })

  console.log('✅ QuotationAnalysisChart series:', {
    open: openValues,
    approved: approvedValues,
    won: wonValues
  })

  return [
    { name: 'Open', data: openValues },
    { name: 'Approved', data: approvedValues },
    { name: 'Won', data: wonValues }
  ]
})

const chartOptions = computed(() => {
  const rawData = deepUnwrap(props.data)
  const trendData = rawData?.trend_data
  
  const categories = Array.isArray(trendData) 
    ? trendData.map(month => month?.month || '') 
    : []

  console.log('📊 QuotationAnalysisChart rendering with categories:', categories)

  return {
    chart: {
      type: 'bar',
      stacked: true,
      toolbar: { show: false },
      height: props.height - 20,
      animations: {
        enabled: true,
        easing: 'easeinout',
        speed: 800
      }
    },
    plotOptions: {
      bar: {
        horizontal: false,
        columnWidth: '50%',
        borderRadius: 6,
        dataLabels: {
          total: {
            enabled: true,
            style: {
              fontSize: '11px',
              fontWeight: 600,
              color: '#111827'
            },
            formatter: formatCurrency,
            offsetY: -35,
            offsetX: 0,
            textAnchor: 'middle'
          }
        }
      }
    },
    dataLabels: { enabled: false },
    stroke: { width: 1, colors: ['transparent'] },
    colors: ['#4F46E5', '#10B981', '#F59E0B'],
    xaxis: {
      categories,
      labels: {
        style: { colors: '#64748B', fontSize: '11px' }
      }
    },
    yaxis: {
      title: { text: 'Value', style: { color: '#64748B' } },
      labels: {
        formatter: formatCurrency,
        style: { colors: '#64748B', fontSize: '11px' }
      }
    },
    tooltip: { 
      enabled: true,
      y: { formatter: formatCurrency } 
    },
    fill: { opacity: 1 },
    legend: { position: 'top', horizontalAlign: 'right' },
    grid: {
      padding: { top: 0, right: 10, left: 10 },
      yaxis: { lines: { show: true } }
    }
  }
})

// Watch for data changes and force re-render
watch(() => props.data, (newVal) => {
  const unwrapped = deepUnwrap(newVal)
  console.log('🔄 QuotationAnalysisChart data changed:', unwrapped)
  chartKey.value++ // Force chart to re-render
}, { deep: true })
</script>

<style scoped>
.chart-container {
  width: 100%;
  min-height: 350px;
}
</style>
