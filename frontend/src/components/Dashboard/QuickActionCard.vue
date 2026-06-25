<template>
  <button
    @click="$emit('click')"
    class="relative flex flex-col items-start p-6 bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow duration-200"
  >
    <div :class="`p-3 rounded-lg mb-4 ${colorClasses[color]}`">
      <FeatherIcon
        :name="iconName"
        class="w-6 h-6 text-white"
      />
    </div>
    <h3 class="text-lg font-semibold text-gray-900 mb-1">{{ title }}</h3>
    <p class="text-sm text-gray-500">{{ description }}</p>
  </button>
</template>

<script>
import { FeatherIcon } from 'frappe-ui'

export default {
  name: 'QuickActionCard',
  components: {
    FeatherIcon
  },
  props: {
    title: {
      type: String,
      required: true
    },
    description: {
      type: String,
      required: true
    },
    icon: {
      type: String,
      required: true
    },
    color: {
      type: String,
      default: 'blue',
      validator: value => ['blue', 'green', 'purple', 'orange'].includes(value)
    }
  },
  computed: {
    iconName() {
      const icons = {
        'plus-circle': 'plus-circle',
        'document-text': 'file-text',
        'document': 'file',
        'calendar': 'calendar'
      }
      return icons[this.icon] || this.icon
    },
    colorClasses() {
      return {
        blue: 'bg-blue-500',
        green: 'bg-green-500',
        purple: 'bg-purple-500',
        orange: 'bg-orange-500'
      }
    }
  }
}
</script> 