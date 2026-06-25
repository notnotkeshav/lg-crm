<template>
  <div class="flex h-full w-full flex-col">
    <!-- Preview Header -->
    <div class="flex items-center justify-between border-b p-4">
      <div class="flex items-center gap-2">
        <component :is="getFileIcon()" class="h-5 w-5 text-gray-600" />
        <span class="text-base font-medium text-gray-900">{{ file?.file_name }}</span>
      </div>
      <div class="flex items-center gap-2">
        <Tooltip :text="__('Download')">
          <Button variant="ghost" @click="downloadFile">
            <DownloadIcon class="h-4 w-4" />
          </Button>
        </Tooltip>
        <Tooltip :text="__('Open in new tab')">
          <Button variant="ghost" @click="openInNewTab">
            <ExternalLinkIcon class="h-4 w-4" />
          </Button>
        </Tooltip>
      </div>
    </div>

    <!-- Preview Content -->
    <div class="relative flex-1 overflow-hidden bg-gray-50">
      <!-- Loading State -->
      <div v-if="loading" class="flex h-full w-full items-center justify-center">
        <div class="flex items-center gap-2 text-gray-600">
          <LoadingIndicator class="h-5 w-5" />
          <span>{{ __('Loading preview...') }}</span>
        </div>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="flex h-full w-full items-center justify-center">
        <div class="text-center text-gray-600">
          <AlertTriangleIcon class="mx-auto mb-2 h-6 w-6 text-yellow-500" />
          <p>{{ __('Preview not available') }}</p>
          <Button class="mt-2" variant="subtle" @click="downloadFile">
            {{ __('Download file instead') }}
          </Button>
        </div>
      </div>

      <!-- Image Preview -->
      <div v-else-if="isImage" class="flex h-full w-full items-center justify-center p-4">
        <img
          :src="file.file_url"
          :alt="file.file_name"
          class="max-h-full max-w-full rounded object-contain"
          @load="loading = false"
          @error="handleError"
        />
      </div>

      <!-- PDF Preview -->
      <div v-else-if="isPdf" class="h-full w-full">
        <iframe
          :src="file.file_url"
          class="h-full w-full border-0"
          style="min-height: calc(80vh - 4rem);"
          frameborder="0"
          @load="loading = false"
          @error="handleError"
        />
      </div>

      <!-- Text Preview -->
      <div
        v-else-if="isText"
        class="h-full w-full overflow-auto p-4 font-mono text-sm"
      >
        {{ content }}
      </div>

      <!-- Fallback Preview -->
      <div v-else class="flex h-full w-full items-center justify-center">
        <div class="text-center text-gray-600">
          <FileIcon class="mx-auto mb-2 h-12 w-12" />
          <p>{{ __('Preview not available for this file type') }}</p>
          <Button class="mt-2" variant="subtle" @click="downloadFile">
            {{ __('Download file') }}
          </Button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Button, Tooltip} from 'frappe-ui'
import mime from 'mime'
import FileIcon from '@/components/Icons/FileIcon.vue'
import FileImageIcon from '@/components/Icons/FileImageIcon.vue'
import FileTextIcon from '@/components/Icons/FileTextIcon.vue'
import FileSpreadsheetIcon from '@/components/Icons/FileSpreadsheetIcon.vue'
import FileAudioIcon from '@/components/Icons/FileAudioIcon.vue'
import FileVideoIcon from '@/components/Icons/FileVideoIcon.vue'
import LoadingIndicator from '@/components/Icons/LoadingIndicator.vue'
import AlertTriangleIcon from '@/components/Icons/AlertTriangleIcon.vue'
import DownloadIcon from '@/components/Icons/DownloadIcon.vue'
import ExternalLinkIcon from '@/components/Icons/ExternalLinkIcon.vue'
import { __ } from '@/translation'

const props = defineProps({
  file: {
    type: Object,
    required: true,
  },
})

const loading = ref(false) // Initialize as false by default
const error = ref(false)
const content = ref('')

const mimeType = computed(() => {
  const extension = props.file.file_name.split('.').pop()?.toLowerCase()
  return mime.getType(extension) || ''
})

const isImage = computed(() => mimeType.value.startsWith('image/'))
const isPdf = computed(() => mimeType.value === 'application/pdf')
const isText = computed(() => mimeType.value === 'text/plain')
const isSpreadsheet = computed(() => mimeType.value.includes('spreadsheet'))
const isAudio = computed(() => mimeType.value.startsWith('audio/'))
const isVideo = computed(() => mimeType.value.startsWith('video/'))

function getFileIcon() {
  if (isText.value) return FileTextIcon
  if (isImage.value) return FileImageIcon
  if (isPdf.value) return FileTextIcon
  if (isSpreadsheet.value) return FileSpreadsheetIcon
  if (isAudio.value) return FileAudioIcon
  if (isVideo.value) return FileVideoIcon
  return FileIcon
}

function handleError() {
  loading.value = false
  error.value = true
}

function downloadFile() {
  const link = document.createElement('a')
  link.href = props.file.file_url
  link.download = props.file.file_name
  link.click()
}

function openInNewTab() {
  window.open(props.file.file_url, '_blank')
}

onMounted(() => {
  // Only set loading true for files that need to be fetched
  if (isText.value) {
    loading.value = true
    fetch(props.file.file_url)
      .then(response => response.text())
      .then(text => {
        content.value = text
        loading.value = false
      })
      .catch(handleError)
  } else if (isImage.value) {
    loading.value = true
    // Preload image
    const img = new Image()
    img.onload = () => {
      loading.value = false
    }
    img.onerror = handleError
    img.src = props.file.file_url
  } else if (isPdf.value) {
    loading.value = true
    // Check if PDF is accessible
    fetch(props.file.file_url, { method: 'HEAD' })
      .then(response => {
        if (!response.ok) throw new Error('PDF not accessible')
        loading.value = false
      })
      .catch(handleError)
  }
})
</script> 