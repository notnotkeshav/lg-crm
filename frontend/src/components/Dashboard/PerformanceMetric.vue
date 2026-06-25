<template>
  <div class="space-y-2">
    <div class="flex items-center justify-between">
      <h4 class="text-sm font-medium text-gray-700">{{ title }}</h4>
      <div
        :class="[
          'flex items-center text-sm',
          trend === 'up' ? 'text-green-600' : 'text-red-600'
        ]"
      >
        <FeatherIcon
          :name="trend === 'up' ? 'arrow-up' : 'arrow-down'"
          class="h-4 w-4 mr-1"
        />
        {{ progress }}%
      </div>
    </div>
    <div class="flex items-center">
      <div class="flex-1">
        <div class="h-2 bg-gray-200 rounded-full">
          <div
            :class="[
              'h-2 rounded-full',
              statusColorClasses[status] || 'bg-gray-500'
            ]"
            :style="{ width: `${progress}%` }"
          />
        </div>
      </div>
      <span class="ml-4 text-sm font-medium text-gray-700">{{ value }}</span>
    </div>
  </div>
</template>

<script>
import { FeatherIcon } from 'frappe-ui'

export default {
  name: 'PerformanceMetric',
  components: {
    FeatherIcon
  },
  props: {
    title: {
      type: String,
      required: true
    },
    value: {
      type: [String, Number],
      required: true
    },
    progress: {
      type: Number,
      required: true
    },
    trend: {
      type: String,
      default: 'up',
      validator: value => ['up', 'down'].includes(value)
    },
    status: {
      type: String,
      default: 'normal',
      validator: value => ['success', 'warning', 'danger', 'normal'].includes(value)
    }
  },
  data() {
    return {
      statusColorClasses: {
        success: 'bg-green-500',
        warning: 'bg-yellow-500',
        danger: 'bg-red-500',
        normal: 'bg-blue-500'
      }
    }
  }
}
</script> 