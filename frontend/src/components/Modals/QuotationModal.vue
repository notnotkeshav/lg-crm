<template>
  <Dialog v-model="show" :options="{ size: '3xl' }">
    <template #body>
      <div class="bg-white px-4 pb-6 pt-5 sm:px-6">
        <div class="mb-5 flex items-center justify-between">
          <div>
            <h3 class="text-2xl font-semibold leading-6 text-gray-900">
              {{ __('Create Quotation') }}
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
              <div>{{ __('Choose Existing Customer') }}</div>
              <Switch v-model="chooseExistingCustomer" />
            </div>
          </div>
          <Fields
            v-if="filteredSections"
            class="border-t pt-4"
            :sections="filteredSections"
            :data="quotation"
          />
          <ErrorMessage class="mt-4" v-if="error" :message="__(error)" />
        </div>
      </div>
      <div class="px-4 pb-7 pt-4 sm:px-6">
        <div class="flex flex-row-reverse gap-2">
          <Button
            variant="solid"
            :label="__('Create')"
            :loading="isQuotationCreating"
            @click="createQuotation"
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
import { createResource } from 'frappe-ui'
import { computed, ref, reactive, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { Switch } from 'frappe-ui'

const props = defineProps({
  defaults: Object,
})

const { getUser, isManager } = usersStore()

const show = defineModel()
const router = useRouter()
const error = ref(null)

const quotation = reactive({
  title: '',
  series: '',
  customer: '',
  customer_name: '',
  date: new Date().toISOString().split('T')[0],
  status: 'Draft',
  company: '',
  amount: 0,
  currency: 'INR',
  terms_and_conditions: '',
  notes: '',
  valid_till: '',
  deal_type: '',
})

const isQuotationCreating = ref(false)
const chooseExistingCustomer = ref(false)

const sections = createResource({
  url: 'crm.fcrm.doctype.crm_fields_layout.crm_fields_layout.get_fields_layout',
  cache: ['quickEntryFields', 'CRM Quotation'],
  params: { doctype: 'CRM Quotation', type: 'Quick Entry' },
  auto: true,
  transform: (data) => {
    if (!data) {
      return [{
        label: 'Quotation Details',
        fields: [
          { name: 'title', label: 'Title', type: 'Data', mandatory: 1 },
          { name: 'customer', label: 'Customer', type: 'Link', options: 'Customer', mandatory: 1 },
          { name: 'date', label: 'Date', type: 'Date', mandatory: 1 },
          { name: 'status', label: 'Status', type: 'Select', options: 'Draft\nSubmitted\nCancelled', default: 'Draft' },
          { name: 'company', label: 'Company', type: 'Link', options: 'Company', mandatory: 1 },
          { name: 'amount', label: 'Amount', type: 'Currency' },
          { name: 'currency', label: 'Currency', type: 'Link', options: 'Currency' },
          { name: 'valid_till', label: 'Valid Till', type: 'Date', mandatory: 1 },
          { name: 'deal_type', label: 'Deal Type', type: 'Select', options: 'Product\nService\nSubscription' },
          { name: 'terms_and_conditions', label: 'Terms and Conditions', type: 'Text Editor' },
          { name: 'notes', label: 'Notes', type: 'Small Text' }
        ]
      }]
    }
    return data
  }
})

const filteredSections = computed(() => {
  let allSections = sections.data || []
  if (!allSections.length) return []

  let _filteredSections = []

  if (chooseExistingCustomer.value) {
    _filteredSections.push(
      allSections.find((s) => s.label === 'Select Customer')
    )
  } else {
    _filteredSections.push(
      allSections.find((s) => s.label === 'Customer Details')
    )
  }

  allSections.forEach((s) => {
    if (!['Select Customer', 'Customer Details'].includes(s.label)) {
      _filteredSections.push(s)
    }
  })

  return _filteredSections
})

function createQuotation() {
  createResource({
    url: 'frappe.client.insert',
    params: {
      doc: {
        doctype: 'CRM Quotation',
        ...quotation
      }
    },
    auto: true,
    validate() {
      error.value = null
      if (!quotation.title) {
        error.value = __('Title is required')
        return error.value
      }
      if (!quotation.customer) {
        error.value = __('Customer is required')
        return error.value
      }
      if (!quotation.date) {
        error.value = __('Date is required')
        return error.value
      }
      if (!quotation.company) {
        error.value = __('Company is required')
        return error.value
      }
      if (!quotation.valid_till) {
        error.value = __('Valid Till date is required')
        return error.value
      }
      isQuotationCreating.value = true
    },
    onSuccess(doc) {
      isQuotationCreating.value = false
      show.value = false
      router.push({ name: 'Quotation', params: { quotationId: doc.name } })
    },
    onError(err) {
      isQuotationCreating.value = false
      error.value = err.messages ? err.messages.join('\n') : err.message
    },
  })
}

const showQuickEntryModal = defineModel('quickEntry')

function openQuickEntryModal() {
  showQuickEntryModal.value = true
  nextTick(() => {
    show.value = false
  })
}

onMounted(() => {
  Object.assign(quotation, props.defaults)
  if (!quotation.status) {
    quotation.status = 'Draft'
  }
})
</script>
