<!-- DealTypeDistributionChart.vue -->
<template>
  <div class="relative h-[300px] w-full">
    <canvas ref="chartRef"></canvas>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import Chart from 'chart.js/auto'

const props = defineProps({
  data: {
    type: Array,
    required: true
  }
})

const chartRef = ref(null)
let chart = null

const createChart = () => {
  if (!chartRef.value || !props.data.length) return

  const ctx = chartRef.value.getContext('2d')
  if (chart) chart.destroy()

  const types = props.data.map(item => item.type)
  const counts = props.data.map(item => item.count)

  // Predefined colors for deal types
  const colors = [
    'rgba(59, 130, 246, 0.8)', // blue
    'rgba(16, 185, 129, 0.8)', // green
    'rgba(245, 158, 11, 0.8)', // yellow
    'rgba(239, 68, 68, 0.8)',  // red
    'rgba(99, 102, 241, 0.8)'  // indigo
  ]

  chart = new Chart(ctx, {
    type: 'pie',
    data: {
      labels: types,
      datasets: [{
        data: counts,
        backgroundColor: colors.slice(0, types.length),
        borderColor: 'white',
        borderWidth: 2
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'right',
          align: 'center'
        },
        tooltip: {
          callbacks: {
            label: context => {
              const label = context.label || ''
              const value = context.raw
              const total = context.dataset.data.reduce((a, b) => a + b, 0)
              const percentage = ((value / total) * 100).toFixed(1)
              return `${label}: ${value} deals (${percentage}%)`
            }
          }
        }
      }
    }
  })
}

watch(() => props.data, createChart, { deep: true })

onMounted(createChart)
</script> 