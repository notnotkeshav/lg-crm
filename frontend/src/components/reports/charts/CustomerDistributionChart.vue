<template>
  <div class="h-[300px] relative">
    <Bar
      v-if="chartData"
      :data="chartData"
      :options="chartOptions"
    />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Bar } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js'

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
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
      label: __('Number of Quotations'),
      data: props.data.map(item => item.value),
      backgroundColor: '#10B981',
      borderRadius: 4
    }
  ]
}))

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  indexAxis: 'y',
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
      grid: {
        display: false
      },
      ticks: {
        color: '#6B7280'
      }
    },
    x: {
      beginAtZero: true,
      grid: {
        color: '#E5E7EB'
      },
      ticks: {
        color: '#6B7280',
        stepSize: 1
      }
    }
  }
}
</script> 