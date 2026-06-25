<!-- DateRangeFilter.vue -->
<template>
  <div class="relative">
    <Listbox v-model="selectedRange" as="div" class="relative">
      <ListboxButton class="relative w-48 cursor-pointer rounded-md bg-white py-1.5 pl-3 pr-10 text-left text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 sm:text-sm sm:leading-6">
        <span class="block truncate">{{ selectedRange }}</span>
        <span class="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-2">
          <ChevronUpDownIcon class="h-5 w-5 text-gray-400" aria-hidden="true" />
        </span>
      </ListboxButton>

      <transition
        leave-active-class="transition ease-in duration-100"
        leave-from-class="opacity-100"
        leave-to-class="opacity-0"
      >
        <ListboxOptions class="absolute z-10 mt-1 max-h-60 w-full overflow-auto rounded-md bg-white py-1 text-base shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none sm:text-sm">
          <ListboxOption
            v-for="range in dateRanges"
            :key="range"
            :value="range"
            v-slot="{ active, selected }"
            as="template"
          >
            <li
              :class="[
                active ? 'bg-blue-600 text-white' : 'text-gray-900',
                'relative cursor-pointer select-none py-2 pl-3 pr-9'
              ]"
            >
              <span :class="[selected ? 'font-semibold' : 'font-normal', 'block truncate']">
                {{ range }}
              </span>

              <span
                v-if="selected"
                :class="[
                  active ? 'text-white' : 'text-blue-600',
                  'absolute inset-y-0 right-0 flex items-center pr-4'
                ]"
              >
                <CheckIcon class="h-5 w-5" aria-hidden="true" />
              </span>
            </li>
          </ListboxOption>
        </ListboxOptions>
      </transition>
    </Listbox>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { Listbox, ListboxButton, ListboxOptions, ListboxOption } from '@headlessui/vue'
import { CheckIcon, ChevronUpDownIcon } from '@heroicons/vue/20/solid'

const dateRanges = [
  'Last Week',
  'Last Month',
  'Last Quarter',
  'Last 6 Months',
  'Last Year',
  'Custom Range'
]

const selectedRange = ref('Last 6 Months')

const emit = defineEmits(['filter-changed'])

watch(selectedRange, (newRange) => {
  emit('filter-changed', newRange)
})
</script> 