<template>
  <div class="flow-root">
    <ul role="list" class="-mb-8">
      <li v-for="(activity, index) in activities" :key="activity.id">
        <div class="relative pb-8">
          <span
            v-if="index !== activities.length - 1"
            class="absolute top-4 left-4 -ml-px h-full w-0.5 bg-gray-200"
            aria-hidden="true"
          />
          <div class="relative flex space-x-3">
            <div>
              <span
                :class="[
                  'h-8 w-8 rounded-full flex items-center justify-center ring-8 ring-white',
                  activityTypeClasses[activity.type] || 'bg-gray-500'
                ]"
              >
                <FeatherIcon
                  :name="activityTypeIcons[activity.type] || 'activity'"
                  class="h-5 w-5 text-white"
                />
              </span>
            </div>
            <div class="flex min-w-0 flex-1 justify-between space-x-4 pt-1.5">
              <div>
                <p class="text-sm text-gray-500">
                  {{ activity.description }}
                  <a
                    v-if="activity.link"
                    :href="activity.link"
                    class="font-medium text-gray-900 hover:text-gray-700"
                  >
                    {{ activity.linkText }}
                  </a>
                </p>
              </div>
              <div class="whitespace-nowrap text-right text-sm text-gray-500">
                <time :datetime="activity.date">{{ formatDate(activity.date) }}</time>
              </div>
            </div>
          </div>
        </div>
      </li>
    </ul>
  </div>
</template>

<script>
import { FeatherIcon } from 'frappe-ui'

export default {
  name: 'ActivityTimeline',
  components: {
    FeatherIcon
  },
  props: {
    activities: {
      type: Array,
      required: true,
      default: () => []
    }
  },
  data() {
    return {
      activityTypeClasses: {
        deal: 'bg-blue-500',
        quotation: 'bg-green-500',
        contract: 'bg-purple-500',
        meeting: 'bg-orange-500',
        call: 'bg-yellow-500'
      },
      activityTypeIcons: {
        deal: 'briefcase',
        quotation: 'file-text',
        contract: 'file',
        meeting: 'calendar',
        call: 'phone'
      }
    }
  },
  methods: {
    formatDate(date) {
      return new Date(date).toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric'
      })
    }
  }
}
</script> 