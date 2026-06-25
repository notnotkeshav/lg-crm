<template>
  <div class="bg-white rounded-lg shadow p-4 hover:shadow-lg transition-shadow duration-200">
    <div class="flex items-start justify-between">
      <div>
        <p class="text-sm font-medium text-gray-600">{{ title }}</p>
        <p class="mt-2 text-2xl font-semibold text-gray-900">{{ formattedValue }}</p>
      </div>
      <div :class="[`bg-${iconColor}-100`, 'rounded-full p-2']">
        <component 
          :is="iconComponent" 
          class="w-5 h-5" 
          :class="`text-${iconColor}-600`" 
          aria-hidden="true" 
        />
      </div>
    </div>
    <div class="mt-4 flex items-center">
      <div :class="[
        change >= 0 ? 'text-green-600 bg-green-100' : 'text-red-600 bg-red-100',
        'inline-flex items-center px-2 py-0.5 rounded-full text-sm font-medium'
      ]">
        <component 
          :is="change >= 0 ? 'ArrowUpIcon' : 'ArrowDownIcon'"
          class="w-4 h-4 mr-1"
          aria-hidden="true"
        />
        {{ Math.abs(change) }}%
      </div>
      <span class="ml-2 text-sm text-gray-500">vs last period</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import {
  CurrencyDollarIcon,
  ChartBarIcon,
  ScaleIcon,
  BriefcaseIcon,
  ArrowUpIcon,
  ArrowDownIcon
} from '@heroicons/vue/24/outline'

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
    required: true
  },
  icon: {
    type: String,
    required: true
  }
})

const iconMap = {
  'currency-dollar': CurrencyDollarIcon,
  'chart-bar': ChartBarIcon,
  'scale': ScaleIcon,
  'briefcase': BriefcaseIcon
}

const iconComponent = computed(() => iconMap[props.icon])

const iconColor = computed(() => {
  const colorMap = {
    'currency-dollar': 'green',
    'chart-bar': 'blue',
    'scale': 'purple',
    'briefcase': 'orange'
  }
  return colorMap[props.icon] || 'gray'
})

const formattedValue = computed(() => {
  if (typeof props.value === 'number') {
    if (props.icon === 'currency-dollar') {
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'INR',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
      }).format(props.value)
    }
    return new Intl.NumberFormat('en-US').format(props.value)
  }
  return props.value
})
</script> 