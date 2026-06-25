<!-- TerritoryDistributionChart.vue -->
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

  const territories = props.data.map(item => item.territory)
  const values = props.data.map(item => item.value)

  // Generate colors for each territory
  const colors = territories.map((_, index) => {
    const hue = (index * 137.5) % 360 // Golden angle approximation
    return `hsl(${hue}, 70%, 60%)`
  })

  chart = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: territories,
      datasets: [{
        data: values,
        backgroundColor: colors,
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
              const value = new Intl.NumberFormat('en-IN', {
                style: 'currency',
                currency: 'INR',
                minimumFractionDigits: 0,
                maximumFractionDigits: 0
              }).format(context.raw)
              const total = context.dataset.data.reduce((a, b) => a + b, 0)
              const percentage = ((context.raw / total) * 100).toFixed(1)
              return `${label}: ${value} (${percentage}%)`
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