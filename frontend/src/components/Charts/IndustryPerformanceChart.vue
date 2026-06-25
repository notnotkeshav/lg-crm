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
  data: { type: Array, required: true }
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
  const isValid = Array.isArray(rawData) && rawData.length > 0
  console.log('📊 IndustryPerformanceChart hasValidData:', isValid, rawData)
  return isValid
})

const series = computed(() => {
  const rawData = deepUnwrap(props.data)
  
  if (!Array.isArray(rawData) || rawData.length === 0) {
    console.warn('⚠️ IndustryPerformanceChart: No valid data')
    return []
  }

  const chartData = rawData.map(item => ({
    name: 'Deals',
    x: item?.industry || 'Unknown',
    y: Number(item?.deal_count) || 0,
    deal_count: item?.deal_count || 0,
    win_rate: Number(item?.win_rate) || 0
  }))

  console.log('✅ IndustryPerformanceChart series:', chartData)

  return [{
    name: 'Revenue',
    data: chartData
  }]
})

const chartOptions = computed(() => {
  const rawData = deepUnwrap(props.data)
  const categories = Array.isArray(rawData) 
    ? rawData.map(item => item?.industry || 'Unknown')
    : []

  console.log('📊 IndustryPerformanceChart rendering with categories:', categories)

  return {
    chart: {
      type: 'bar',
      toolbar: { show: false },
      animations: {
        enabled: true,
        easing: 'easeinout',
        speed: 800
      }
    },
    plotOptions: {
      bar: {
        horizontal: true,
        columnWidth: '55%',
        borderRadius: 8,
        distributed: true,
        dataLabels: {
          position: 'top'
        }
      }
    },
    dataLabels: {
      enabled: true,
      formatter: function (val, { dataPointIndex, w }) {
        const data = w.globals.initialSeries[0].data[dataPointIndex]
        return `${formatCurrency(val)} (${data.win_rate}% Win Rate)`
      },
      style: {
        fontSize: '12px',
        colors: ['#64748B']
      },
      offsetX: 30
    },
    legend: {
      show: true,
      position: 'bottom',
      horizontalAlign: 'right',
      fontSize: '12px',
      itemMargin: {
        horizontal: 10,
        vertical: 5
      },
      markers: {
        width: 12,
        height: 12,
        radius: 2
      }
    },
    xaxis: {
      categories,
      labels: {
        style: {
          fontSize: '12px',
          fontWeight: 500,
          colors: '#64748B'
        }
      }
    },
    yaxis: {
      title: {
        text: 'Industry',
        style: {
          color: '#64748B'
        }
      },
      labels: {
        style: {
          colors: '#64748B'
        }
      }
    },
    colors: ['#4F46E5', '#10B981', '#6366F1', '#EC4899', '#F59E0B', '#3B82F6', '#8B5CF6', '#14B8A6', '#06B6D4', '#0EA5E9'],
    fill: {
      type: 'gradient',
      gradient: {
        shade: 'light',
        type: 'horizontal',
        shadeIntensity: 0.25,
        inverseColors: true,
        opacityFrom: 0.85,
        opacityTo: 0.85,
        stops: [50, 0, 100]
      }
    },
    tooltip: {
      enabled: true,
      shared: false,
      y: {
        formatter: function (val) {
          return formatCurrency(val)
        }
      },
      custom: function ({ series, seriesIndex, dataPointIndex, w }) {
        const data = w.globals.initialSeries[0].data[dataPointIndex]
        return `
          <div class="p-2">
            <div class="font-medium">${w.globals.labels[dataPointIndex]}</div>
            <div>Revenue: ${formatCurrency(series[seriesIndex][dataPointIndex])}</div>
            <div>Deals: ${data.deal_count}</div>
            <div>Win Rate: ${data.win_rate}%</div>
          </div>
        `
      }
    }
  }
})

// Watch for data changes and force re-render
watch(() => props.data, (newVal) => {
  const unwrapped = deepUnwrap(newVal)
  console.log('🔄 IndustryPerformanceChart data changed:', unwrapped)
  chartKey.value++ // Force chart to re-render
}, { deep: true })
</script>

<style scoped>
.chart-container {
  width: 100%;
  min-height: 350px;
}
</style>
