<template>
  <Dialog
    v-model="show"
    :options="{
      size: '5xl',
      title: file?.file_name,
    }"
  >
    <template #actions>
      <div class="flex gap-2">
        <Button
          v-if="file?.is_private !== undefined"
          variant="subtle"
          @click="togglePrivate"
        >
          <template #prefix>
            <FeatherIcon
              :name="file.is_private ? 'lock' : 'unlock'"
              class="h-4 w-4"
            />
          </template>
          {{ file.is_private ? __('Make public') : __('Make private') }}
        </Button>
        <Button variant="subtle" theme="red" @click="deleteFile">
          <template #prefix>
            <FeatherIcon name="trash-2" class="h-4 w-4" />
          </template>
          {{ __('Delete') }}
        </Button>
      </div>
    </template>
    <template #body-content>
      <div class="h-[70vh]">
        <AttachmentPreview :file="file" />
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Dialog, Button, FeatherIcon} from 'frappe-ui'
import { globalStore } from '@/stores/global'
import { __ } from '@/translation'
import AttachmentPreview from './AttachmentPreview.vue'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false,
  },
  file: {
    type: Object,
    required: true,
  },
})

const emit = defineEmits(['update:modelValue', 'delete', 'toggle-private'])

const show = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value),
})

const { $dialog, call } = globalStore()

function togglePrivate() {
  let changeTo = props.file.is_private ? __('public') : __('private')
  let title = __('Make attachment {0}', [changeTo])
  let message = __('Are you sure you want to make this attachment {0}?', [changeTo])
  
  $dialog({
    title,
    message,
    actions: [
      {
        label: __('Make {0}', [changeTo]),
        variant: 'solid',
        onClick: async (close) => {
          await call('frappe.client.set_value', {
            doctype: 'File',
            name: props.file.name,
            fieldname: {
              is_private: !props.file.is_private,
            },
          })
          emit('toggle-private')
          close()
        },
      },
    ],
  })
}

function deleteFile() {
  $dialog({
    title: __('Delete attachment'),
    message: __('Are you sure you want to delete this attachment?'),
    actions: [
      {
        label: __('Delete'),
        variant: 'solid',
        theme: 'red',
        onClick: async (close) => {
          await call('frappe.client.delete', {
            doctype: 'File',
            name: props.file.name,
          })
          emit('delete')
          close()
        },
      },
    ],
  })
}
</script> 