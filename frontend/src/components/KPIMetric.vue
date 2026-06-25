<template>
  <div class="flex flex-col">
    <div class="flex items-center justify-between">
      <div class="flex items-center space-x-2">
        <FeatherIcon 
          :name="icon" 
          class="w-5 h-5" 
          :class="{
            'text-blue-600': color === 'blue',
            'text-green-600': color === 'green',
            'text-purple-600': color === 'purple',
            'text-orange-600': color === 'orange',
            'text-red-600': color === 'red'
          }"
        />
        <span class="text-sm font-medium text-gray-500">{{ title }}</span>
      </div>
      <div class="flex items-center space-x-2">
        <span 
          v-if="growth !== undefined" 
          class="flex items-center text-sm font-medium"
          :class="{
            'text-green-600': growth > 0,
            'text-red-600': growth < 0,
            'text-gray-500': growth === 0
          }"
        >
          <FeatherIcon 
            :name="growth > 0 ? 'trending-up' : growth < 0 ? 'trending-down' : 'minus'" 
            class="w-4 h-4 mr-1"
          />
          {{ Math.abs(growth).toFixed(1) }}%
        </span>
      </div>
    </div>
    <div class="mt-2">
      <span class="text-2xl font-semibold text-gray-900">{{ value }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { FeatherIcon } from 'frappe-ui'

defineProps({
  title: {
    type: String,
    required: true
  },
  value: {
    type: [String, Number],
    required: true
  },
  growth: {
    type: Number,
    default: undefined
  },
  icon: {
    type: String,
    required: true
  },
  color: {
    type: String,
    default: 'blue',
    validator: (value: string) => ['blue', 'green', 'purple', 'orange', 'red'].includes(value)
  }
})
</script> 