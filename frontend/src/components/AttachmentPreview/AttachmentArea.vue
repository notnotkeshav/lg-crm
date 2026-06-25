<template>
  <div class="flex flex-col gap-4">
    <!-- Single Attachment Direct Preview -->
    <div v-if="attachments?.length === 1" class="min-h-[80vh] rounded-lg border bg-white">
      <AttachmentPreview :file="attachments[0]" />
    </div>

    <!-- Multiple Attachments -->
    <div v-else-if="attachments?.length > 1" class="flex flex-col gap-4">
      <!-- Selected Attachment Preview -->
      <div v-if="selectedFile" class="min-h-[80vh] rounded-lg border bg-white">
        <AttachmentPreview :file="selectedFile" />
      </div>

      <!-- Attachment List -->
      <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <div
          v-for="file in attachments"
          :key="file.name"
          class="group relative flex cursor-pointer items-center gap-3 rounded-lg border bg-white p-3 hover:border-blue-500"
          :class="{ 'border-blue-500 ring-1 ring-blue-500': selectedFile?.name === file.name }"
          @click="selectFile(file)"
        >
          <component :is="getFileIcon(file)" class="h-8 w-8 flex-shrink-0 text-gray-500" />
          <div class="min-w-0 flex-1">
            <p class="truncate text-sm font-medium text-gray-900">{{ file.file_name }}</p>
            <p class="text-xs text-gray-500">{{ formatFileInfo(file) }}</p>
          </div>
          <div class="flex items-center gap-2">
            <Button
              v-if="file.is_private !== undefined"
              variant="ghost"
              class="opacity-0 group-hover:opacity-100"
              @click.stop="togglePrivate(file)"
            >
              <FeatherIcon
                :name="file.is_private ? 'lock' : 'unlock'"
                class="h-4 w-4"
              />
            </Button>
            <Button
              variant="ghost"
              class="opacity-0 group-hover:opacity-100"
              @click.stop="deleteFile(file)"
            >
              <FeatherIcon name="trash-2" class="h-4 w-4 text-red-500" />
            </Button>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div
      v-else
      class="flex h-32 flex-col items-center justify-center gap-2 rounded-lg border-2 border-dashed border-gray-200 bg-gray-50 p-4 text-center"
    >
      <AttachmentIcon class="h-8 w-8 text-gray-400" />
      <div class="text-sm text-gray-600">
        {{ __('No attachments yet') }}
      </div>
      <Button variant="subtle" @click="$emit('add')">
        {{ __('Add attachment') }}
      </Button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Button, FeatherIcon} from 'frappe-ui'
import { globalStore } from '@/stores/global'
import { formatFileSize, formatDate} from '@/utils'
import AttachmentIcon from '@/components/Icons/AttachmentIcon.vue'
import FileIcon from '@/components/Icons/FileIcon.vue'
import FileImageIcon from '@/components/Icons/FileImageIcon.vue'
import FileTextIcon from '@/components/Icons/FileTextIcon.vue'
import FileSpreadsheetIcon from '@/components/Icons/FileSpreadsheetIcon.vue'
import FileAudioIcon from '@/components/Icons/FileAudioIcon.vue'
import FileVideoIcon from '@/components/Icons/FileVideoIcon.vue'
import AttachmentPreview from './AttachmentPreview.vue'
import { __ } from '@/translation'
import mime from 'mime'

const props = defineProps({
  attachments: {
    type: Array,
    default: () => [],
    required: true,
  },
})

const emit = defineEmits(['reload', 'add'])
const { $dialog, call } = globalStore()

// Selected file state
const selectedFile = ref(null)

// Initialize with latest file if multiple attachments
onMounted(() => {
  if (props.attachments?.length > 1) {
    // Sort by creation date and select the latest
    const sortedFiles = [...props.attachments].sort((a, b) => 
      new Date(b.creation) - new Date(a.creation)
    )
    selectedFile.value = sortedFiles[0]
  }
})

function selectFile(file) {
  selectedFile.value = file
}

function getFileIcon(file) {
  const extension = file.file_name.split('.').pop()?.toLowerCase()
  const mimeType = mime.getType(extension) || ''

  if (mimeType.startsWith('image/')) return FileImageIcon
  if (mimeType === 'application/pdf') return FileTextIcon
  if (mimeType === 'text/plain') return FileTextIcon
  if (mimeType.includes('spreadsheet')) return FileSpreadsheetIcon
  if (mimeType.startsWith('audio/')) return FileAudioIcon
  if (mimeType.startsWith('video/')) return FileVideoIcon
  return FileIcon
}

function formatFileInfo(file) {
  return `${formatFileSize(file.file_size)} · ${formatDate(file.creation)}`
}

function togglePrivate(file) {
  let changeTo = file.is_private ? __('public') : __('private')
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
            name: file.name,
            fieldname: {
              is_private: !file.is_private,
            },
          })
          emit('reload')
          close()
        },
      },
    ],
  })
}

function deleteFile(file) {
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
            name: file.name,
          })
          emit('reload')
          close()
        },
      },
    ],
  })
}
</script> 