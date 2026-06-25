<template>
  <Transition name="slide">
    <div
      v-if="modelValue"
      class="fixed inset-0 z-50 overflow-hidden"
      @click="closePanel"
    >
      <div class="absolute inset-0 overflow-hidden">
        <div class="absolute inset-0 bg-gray-500 bg-opacity-75 transition-opacity" />
        <div class="fixed inset-y-0 right-0 flex max-w-full pl-10">
          <div class="relative w-screen max-w-md">
            <div
              class="flex h-full flex-col overflow-y-auto bg-white shadow-xl"
              @click.stop
            >
              <!-- Header -->
              <div class="flex items-center justify-between border-b px-4 py-3">
                <h2 class="text-lg font-medium text-gray-900">{{ title }}</h2>
                <button
                  class="rounded-md text-gray-400 hover:text-gray-500"
                  @click="closePanel"
                >
                  <FeatherIcon name="x" class="h-5 w-5" />
                </button>
              </div>

              <!-- Body -->
              <div class="flex-1">
                <slot name="body"></slot>
              </div>

              <!-- Footer -->
              <div class="flex justify-end gap-2 border-t px-4 py-3">
                <slot name="actions">
                  <Button variant="secondary" @click="closePanel">
                    {{ __('Cancel') }}
                  </Button>
                  <Button variant="solid" @click="$emit('save')">
                    {{ __('Save') }}
                  </Button>
                </slot>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { FeatherIcon, Button } from 'frappe-ui'

defineProps({
  modelValue: {
    type: Boolean,
    required: true
  },
  title: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['update:modelValue', 'save'])

function closePanel() {
  emit('update:modelValue', false)
}
</script>

<style scoped>
.slide-enter-active,
.slide-leave-active {
  transition: transform 0.3s ease-out;
}

.slide-enter-from,
.slide-leave-to {
  transform: translateX(100%);
}

.slide-enter-to,
.slide-leave-from {
  transform: translateX(0);
}
</style> 