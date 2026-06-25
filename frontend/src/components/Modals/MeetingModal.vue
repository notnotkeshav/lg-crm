<template>
  <Dialog v-model="show" :options="{ size: '3xl' }">
    <template #body>
      <div class="bg-white px-4 pb-6 pt-5 sm:px-6">
        <div class="mb-5 flex items-center justify-between">
          <div>
            <h3 class="text-2xl font-semibold leading-6 text-gray-900">
              {{ __('Schedule Meeting') }}
            </h3>
          </div>
          <div class="flex items-center gap-1">
            <Button variant="ghost" class="w-7" @click="show = false">
              <FeatherIcon name="x" class="h-4 w-4" />
            </Button>
          </div>
        </div>

        <div>
          <form @submit.prevent="handleSubmit" class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700">Title</label>
              <input
                type="text"
                v-model="formData.title"
                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                required
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700">Date & Time</label>
              <input
                type="datetime-local"
                v-model="formData.datetime"
                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                required
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700">Duration (minutes)</label>
              <input
                type="number"
                v-model="formData.duration"
                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                min="15"
                step="15"
                required
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700">Description</label>
              <textarea
                v-model="formData.description"
                rows="3"
                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              ></textarea>
            </div>
          </form>
        </div>
      </div>
      <div class="px-4 pb-7 pt-4 sm:px-6">
        <div class="flex flex-row-reverse gap-2">
          <Button
            variant="solid"
            :label="__('Schedule')"
            :loading="createMeeting.loading"
            @click="handleSubmit"
          />
          <Button
            variant="outline"
            :label="__('Cancel')"
            @click="show = false"
          />
        </div>
      </div>
    </template>
  </Dialog>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { createResource } from 'frappe-ui'

const show = defineModel()

const formData = ref({
  title: '',
  datetime: '',
  duration: 30,
  description: ''
})

const createMeeting = createResource({
  url: 'crm.api.meeting.create_meeting',
  onSuccess() {
    show.value = false
    formData.value = {
      title: '',
      datetime: '',
      duration: 30,
      description: ''
    }
  }
})

const handleSubmit = () => {
  createMeeting.submit(formData.value)
}
</script> 