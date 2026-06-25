<!-- DealPipelineChart.vue -->
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

  const stages = props.data.map(item => item.stage)
  const values = props.data.map(item => item.value)
  const counts = props.data.map(item => item.count)

  chart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: stages,
      datasets: [
        {
          label: 'Deal Value',
          data: values,
          backgroundColor: 'rgba(59, 130, 246, 0.5)',
          borderColor: 'rgb(59, 130, 246)',
          borderWidth: 1,
          yAxisID: 'y'
        },
        {
          label: 'Number of Deals',
          data: counts,
          backgroundColor: 'rgba(99, 102, 241, 0.5)',
          borderColor: 'rgb(99, 102, 241)',
          borderWidth: 1,
          yAxisID: 'y1'
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          type: 'linear',
          position: 'left',
          title: {
            display: true,
            text: 'Deal Value (₹)'
          },
          ticks: {
            callback: value => {
              return new Intl.NumberFormat('en-IN', {
                style: 'currency',
                currency: 'INR',
                notation: 'compact'
              }).format(value)
            }
          }
        },
        y1: {
          type: 'linear',
          position: 'right',
          title: {
            display: true,
            text: 'Number of Deals'
          },
          grid: {
            drawOnChartArea: false
          }
        }
      },
      plugins: {
        tooltip: {
          callbacks: {
            label: context => {
              const label = context.dataset.label
              const value = context.datasetIndex === 0
                ? new Intl.NumberFormat('en-IN', {
                    style: 'currency',
                    currency: 'INR'
                  }).format(context.raw)
                : context.raw
              return `${label}: ${value}`
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