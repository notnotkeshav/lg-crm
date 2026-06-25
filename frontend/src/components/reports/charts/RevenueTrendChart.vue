<!-- RevenueTrendChart.vue -->
<template>
  <div class="h-[300px] relative">
    <Line
      v-if="chartData"
      :data="chartData"
      :options="chartOptions"
    />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
)

const props = defineProps({
  data: {
    type: Array,
    default: () => []
  }
})

const chartData = computed(() => ({
  labels: props.data.map(item => item.label),
  datasets: [
    {
      label: __('Revenue'),
      data: props.data.map(item => item.value),
      borderColor: '#10B981',
      backgroundColor: '#10B98120',
      fill: true,
      tension: 0.4,
      pointRadius: 4,
      pointBackgroundColor: '#10B981'
    }
  ]
}))

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false
    },
    tooltip: {
      backgroundColor: '#1F2937',
      titleColor: '#F3F4F6',
      bodyColor: '#F3F4F6',
      padding: 12,
      borderColor: '#374151',
      borderWidth: 1,
      displayColors: false
    }
  },
  scales: {
    y: {
      beginAtZero: true,
      grid: {
        color: '#E5E7EB'
      },
      ticks: {
        color: '#6B7280'
      }
    },
    x: {
      grid: {
        display: false
      },
      ticks: {
        color: '#6B7280'
      }
    }
  }
}
</script> 