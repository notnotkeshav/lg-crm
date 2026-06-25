<template>
  <Dialog v-model="show" :options="{ size: '3xl' }">
    <template #body>
      <div class="bg-white px-4 pb-6 pt-5 sm:px-6">
        <div class="mb-5 flex items-center justify-between">
          <div>
            <h3 class="text-2xl font-semibold leading-6 text-gray-900">
              {{ __('Create Serial No.') }}
            </h3>
          </div>
          <div class="flex items-center gap-1">
            <Button
              v-if="isManager()"
              variant="ghost"
              class="w-7"
              @click="openQuickEntryModal"
            >
              <EditIcon class="h-4 w-4" />
            </Button>
            <Button variant="ghost" class="w-7" @click="show = false">
              <FeatherIcon name="x" class="h-4 w-4" />
            </Button>
          </div>
        </div>
        <div>
          <div class="mb-4 grid grid-cols-1 gap-4 sm:grid-cols-3">
            <div class="flex items-center gap-3 text-sm text-gray-600">
              <div>{{ __('Choose Existing Serial No.') }}</div>
              <Switch v-model="chooseExistingSerialNo" />
            </div>
            <div class="flex items-center gap-3 text-sm text-gray-600">
              <div>{{ __('Choose Existing Product') }}</div>
              <Switch v-model="chooseExistingProduct" />
            </div>
          </div>
          <Fields
            v-if="filteredSections"
            class="border-t pt-4"
            :sections="filteredSections"
            :data="serial"
          />
          <ErrorMessage class="mt-4" v-if="error" :message="__(error)" />
        </div>
      </div>
      <div class="px-4 pb-7 pt-4 sm:px-6">
        <div class="flex flex-row-reverse gap-2">
          <Button
            variant="solid"
            :label="__('Create')"
            :loading="isSerialCreating"
            @click="createSerial"
          />
        </div>
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import EditIcon from '@/components/Icons/EditIcon.vue'
import Fields from '@/components/Fields.vue'
import { usersStore } from '@/stores/users'
import { statusesStore } from '@/stores/statuses'
import { capture } from '@/telemetry'
import { Switch } from 'frappe-ui'
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
const frappe = window.frappe;


const props = defineProps({
  defaults: Object,
})

const { isManager } = usersStore()
const { getSerialStatus, statusOptions } = statusesStore()

const show = defineModel()
const router = useRouter()
const error = ref(null)
const isSerialCreating = ref(false)

const serial = reactive({
  serial_no: '',
  product_name: '',
  product_group: '',
  start_date: '',
  expiry_date: '',
  product_code: '',
  status: '',
  type: '',
  warranty_period_in_days: ''
})

const chooseExistingSerialNo = ref(false)
const chooseExistingProduct = ref(false)

const filteredSections = computed(() => {
  // Ensure this is returning relevant sections
  return [
    { label: 'Serial No', value: serial.serial_no },
    { label: 'Status', value: serial.status },
    { label: 'Product Name', value: serial.product_name },
    { label: 'Product Group', value: serial.product_group },
    { label: 'Start Date', value: serial.start_date },
    { label: 'Expiry Date', value: serial.expiry_date },
    { label: 'Product Code', value: serial.product_code },
    { label: 'Type', value: serial.type },
    { label: 'Warranty Period (Days)', value: serial.warranty_period_in_days },
  ]
})

async function createSerial() {
  error.value = null
  if (!serial.status) {
    error.value = __('Status is required')
    return
  }

  isSerialCreating.value = true

  try {
    let response = await frappe.call({
      method: 'crm.fcrm.doctype.serial_no.serial_no.create_serial_no',
      args: { 
        serial_no: serial.serial_no,
        product_name: serial.product_name,
        product_group: serial.product_group,
        start_date: serial.start_date,
        expiry_date: serial.expiry_date,
        product_code: serial.product_code,
        status: serial.status,
        type: serial.type,
        warranty_period_in_days: serial.warranty_period_in_days
      },
    })
    console.log("Response is : ", response);
    if (response && response.message) {
      capture('serial_created')
      isSerialCreating.value = false
      show.value = false
      router.push({ name: 'serial_no', params: { serialId: response.message } })
    } else {
      throw new Error('Unexpected API response')
    }
  } catch (err) {
    isSerialCreating.value = false
    error.value = err.message || 'Error creating serial number'
  }
}
</script>

<style scoped>
</style>
