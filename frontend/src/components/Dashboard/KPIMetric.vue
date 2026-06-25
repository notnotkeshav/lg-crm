<template>
  <div class="flex items-center justify-between p-4 bg-white rounded-lg border border-gray-100 hover:border-gray-200 transition-all duration-200">
    <div class="flex items-start">
      <div :class="`p-2 rounded-lg bg-${color}-100 mr-4`" v-if="icon">
        <FeatherIcon :name="icon" :class="`h-5 w-5 text-${color}-600`" />
      </div>
      <div>
        <h3 class="text-sm font-medium text-gray-500">{{ title }}</h3>
        <div class="mt-1 flex items-baseline">
          <p class="text-2xl font-semibold text-gray-900">{{ value }}</p>
          <p :class="[
            change > 0 ? 'text-green-600' : 'text-red-600',
            'ml-2 flex items-baseline text-sm font-semibold'
          ]">
            <FeatherIcon
              :name="change >= 0 ? 'trending-up' : 'trending-down'"
              class="h-4 w-4 flex-shrink-0 self-center"
            />
            <span class="ml-1">{{ Math.abs(change).toFixed(1) }}%</span>
          </p>
        </div>
      </div>
    </div>
    <div class="ml-4">
      <div class="h-16 w-24">
        <apexchart
          type="area"
          height="100%"
          :options="chartOptions"
          :series="[{ data: trend }]"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { FeatherIcon } from 'frappe-ui'

const props = defineProps({
  title: {
    type: String,
    required: true
  },
  value: {
    type: [String, Number],
    required: true
  },
  change: {
    type: Number,
    default: 0
  },
  trend: {
    type: Array,
    default: () => []
  },
  icon: {
    type: String,
    default: ''
  },
  color: {
    type: String,
    default: 'gray'
  }
})

const chartOptions = computed(() => ({
  chart: {
    type: 'area',
    sparkline: {
      enabled: true
    },
    toolbar: {
      show: false
    },
    animations: {
      enabled: true,
      easing: 'easeinout',
      speed: 800
    }
  },
  stroke: {
    width: 2,
    curve: 'smooth'
  },
  fill: {
    type: 'gradient',
    gradient: {
      shadeIntensity: 1,
      opacityFrom: 0.45,
      opacityTo: 0.05,
      stops: [50, 100]
    }
  },
  colors: [props.change >= 0 ? '#10B981' : '#EF4444'],
  tooltip: {
    fixed: {
      enabled: false
    },
    x: {
      show: false
    },
    y: {
      title: {
        formatter: function(seriesName) {
          return ''
        }
      }
    },
    marker: {
      show: false
    }
  }
}))
</script> 