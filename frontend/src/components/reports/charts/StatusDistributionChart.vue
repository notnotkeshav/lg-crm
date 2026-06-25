<template>
  <div class="h-[300px] relative">
    <Doughnut
      v-if="chartData"
      :data="chartData"
      :options="chartOptions"
    />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Doughnut } from 'vue-chartjs'
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend
} from 'chart.js'

ChartJS.register(
  ArcElement,
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
      data: props.data.map(item => item.value),
      backgroundColor: [
        '#4F46E5', // Indigo
        '#10B981', // Emerald
        '#F59E0B', // Amber
        '#EF4444', // Red
        '#8B5CF6', // Purple
        '#EC4899'  // Pink
      ],
      borderWidth: 0,
      borderRadius: 4
    }
  ]
}))

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'right',
      labels: {
        usePointStyle: true,
        pointStyle: 'circle',
        padding: 20,
        color: '#6B7280'
      }
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
  cutout: '60%'
}
</script> 