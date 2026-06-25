<template>
  <Dialog v-model="show" :options="{ size: '3xl' }">
    <template #body>
      <div class="bg-white px-4 pb-6 pt-5 sm:px-6">
        <div class="mb-5 flex items-center justify-between">
          <div>
            <h3 class="text-2xl font-semibold leading-6 text-gray-900">
              {{ __('Create Contract') }}
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
            :data="contract"
          />
          <ErrorMessage class="mt-4" v-if="error" :message="__(error)" />
        </div>
      </div>
      <div class="px-4 pb-7 pt-4 sm:px-6">
        <div class="flex flex-row-reverse gap-2">
          <Button
            variant="solid"
            :label="__('Create')"
            :loading="isContractCreating"
            @click="createContract"
          />
        </div>
      </div>
    </template>
  </Dialog>

  <!-- Side Panel for Contract Items -->
  <ContractItemPanel
    v-if="showItemEditPanel"
    v-model="showItemEditPanel"
    :item="selectedItem"
    @save="saveItemChanges"
  />
</template>

<script setup>
import EditIcon from '@/components/Icons/EditIcon.vue'
import Fields from '@/components/Fields.vue'
import ContractItemsTable from './ContractItemsTable.vue'
import ContractItemPanel from './ContractItemPanel.vue'
import { usersStore } from '@/stores/users'
import { createResource } from 'frappe-ui'
import { computed, ref, reactive, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { Dialog, Button, Switch } from 'frappe-ui'

const props = defineProps({
  defaults: Object,
})

const { getUser, isManager } = usersStore()

const show = defineModel()
const router = useRouter()
const error = ref(null)
const showItemEditPanel = ref(false)
const selectedItem = ref(null)
const chooseExistingCustomer = ref(false)

const contract = reactive({
  title: '',
  series: '',
  customer: '',
  customer_name: '',
  date: new Date().toISOString().split('T')[0],
  status: 'Draft',
  company: '',
  contract_value: 0,
  currency: '',
  terms_and_conditions: '',
  notes: '',
  contract_from: '',
  deal_type: '',
  serial_no: '',
  product_name: '',
  start_date: '',
  expiry_date: '',
  amc: '',
  amount: 0,
  payment_frequency: '',
  customer_address: '',
  shipping_address: ''
})

const isContractCreating = ref(false)

const sections = createResource({
  url: 'crm.fcrm.doctype.crm_fields_layout.crm_fields_layout.get_fields_layout',
  cache: ['quickEntryFields', 'CRM Contract'],
  params: { doctype: 'CRM Contract', type: 'Quick Entry' },
  auto: true,
  transform: (data) => {
    if (!data) {
      return [{
        label: 'Contract Details',
        fields: [
          { name: 'title', label: 'Title', type: 'Data', mandatory: 1 },
          { name: 'customer', label: 'Customer', type: 'Link', options: 'Customer', mandatory: 1 },
          { name: 'date', label: 'Date', type: 'Date', mandatory: 1 },
          { name: 'status', label: 'Status', type: 'Select', options: 'Draft\nActive\nExpired\nCancelled', default: 'Draft' },
          { name: 'company', label: 'Company', type: 'Link', options: 'Company', mandatory: 1 },
          { name: 'contract_value', label: 'Contract Value', type: 'Currency' },
          { name: 'currency', label: 'Currency', type: 'Link', options: 'Currency' },
          { name: 'terms_and_conditions', label: 'Terms and Conditions', type: 'Text Editor' },
          { name: 'notes', label: 'Notes', type: 'Small Text' },
          { name: 'contract_from', label: 'Contract From', type: 'Date' },
          { name: 'deal_type', label: 'Contract Type', type: 'Select', options: 'New\nAMC\nWarranty' },
          { name: 'serial_no', label: 'Serial No.', type: 'Data' },
          { name: 'product_name', label: 'Product Name', type: 'Data' },
          { name: 'start_date', label: 'Start Date', type: 'Date' },
          { name: 'expiry_date', label: 'Expiry Date', type: 'Date' },
          { name: 'amc', label: 'AMC Price List', type: 'Link', options: 'Price List' },
          { name: 'amount', label: 'Amount', type: 'Currency' },
          { name: 'payment_frequency', label: 'Payment Frequency', type: 'Select', options: 'Monthly\nQuarterly\nHalf-Yearly\nYearly' },
          { name: 'customer_address', label: 'Customer Address', type: 'Link', options: 'Address' },
          { name: 'shipping_address', label: 'Shipping Address', type: 'Link', options: 'Address' }
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

function createContract() {
  createResource({
    url: 'frappe.client.insert',
    params: {
      doc: {
        doctype: 'CRM Contract',
        ...contract
      }
    },
    auto: true,
    validate() {
      error.value = null
      if (!contract.title) {
        error.value = __('Title is required')
        return error.value
      }
      if (!contract.customer) {
        error.value = __('Customer is required')
        return error.value
      }
      if (!contract.date) {
        error.value = __('Date is required')
        return error.value
      }
      if (!contract.company) {
        error.value = __('Company is required')
        return error.value
      }
      isContractCreating.value = true
    },
    onSuccess(doc) {
      isContractCreating.value = false
      show.value = false
      router.push({ name: 'Contract', params: { contractId: doc.name } })
    },
    onError(err) {
      isContractCreating.value = false
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

function editItem(item) {
  selectedItem.value = { ...item }
  showItemEditPanel.value = true
}

function saveItemChanges(item) {
  const index = contract.items.findIndex(i => i.idx === item.idx)
  if (index > -1) {
    contract.items[index] = { ...item }
  } else {
    contract.items.push({ ...item })
  }
}

function handleItemFieldChange(value, fieldname) {
  if (!selectedItem.value) return
  
  selectedItem.value[fieldname] = value
  
  // Calculate amount when rate changes
  if (fieldname === 'rate') {
    selectedItem.value.amount = selectedItem.value.rate
  }
  
  // Fetch serial no details
  if (fieldname === 'serial_no' && value) {
    createResource({
      url: 'frappe.client.get',
      params: {
        doctype: 'Serial No',
        name: value
      },
      auto: true,
      onSuccess: (data) => {
        if (data) {
          selectedItem.value.product_code = data.product_code || ''
          selectedItem.value.product_name = data.product_name || ''
        }
      },
      onError: (err) => {
        console.error('Error fetching serial no details:', err)
      }
    })
  }
}

onMounted(() => {
  Object.assign(contract, props.defaults)
  if (!contract.status) {
    contract.status = 'Draft'
  }
})
</script> 