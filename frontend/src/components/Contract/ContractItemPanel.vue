<template>
  <Dialog v-model="show" :options="{ size: '2xl' }">
    <template #body>
      <div class="bg-white px-4 pb-6 pt-5 sm:px-6">
        <div class="mb-5 flex items-center justify-between">
          <div>
            <h3 class="text-lg font-medium leading-6 text-gray-900">
              {{ __('Edit Contract Item') }}
            </h3>
          </div>
          <div class="flex items-center gap-1">
            <Button variant="ghost" class="w-7" @click="show = false">
              <FeatherIcon name="x" class="h-4 w-4" />
            </Button>
          </div>
        </div>
        <div class="space-y-4">
          <div v-for="field in fields" :key="field.name" class="w-full">
            <template v-if="field.type === 'Link'">
              <Autocomplete
                :label="field.label"
                :placeholder="__('Select {0}', [field.label])"
                :doctype="field.options"
                :required="field.mandatory"
                :read_only="field.read_only"
                v-model="localItem[field.name]"
                @change="(value) => handleFieldChange(field.name, value)"
                class="w-full"
              />
            </template>
            <template v-else-if="field.type === 'Select'">
              <FormControl
                :label="field.label"
                type="select"
                :options="field.options.map(opt => ({ label: opt, value: opt }))"
                :required="field.mandatory"
                :read_only="field.read_only"
                v-model="localItem[field.name]"
                @change="(value) => handleFieldChange(field.name, value)"
                class="w-full"
              />
            </template>
            <template v-else>
              <FormControl
                :label="field.label"
                :type="field.type.toLowerCase()"
                :required="field.mandatory"
                :read_only="field.read_only"
                v-model="localItem[field.name]"
                @change="(value) => handleFieldChange(field.name, value)"
                class="w-full"
              />
            </template>
          </div>
        </div>
      </div>
    </template>
    <template #actions>
      <div class="flex justify-end gap-2 px-4 py-3">
        <Button variant="secondary" @click="show = false">
          {{ __('Cancel') }}
        </Button>
        <Button variant="primary" @click="saveChanges">
          {{ __('Save') }}
        </Button>
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import { FormControl, Autocomplete, createResource, Dialog, Button, FeatherIcon } from 'frappe-ui'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  item: {
    type: Object,
    default: () => ({})
  },
  parentDoc: {
    type: Object,
    default: () => ({
      doctype: 'CRM Contract',
      name: 'new'
    })
  }
})

const emit = defineEmits(['update:modelValue', 'save'])

const show = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const localItem = ref({
  doctype: 'CRM Contract Item',
  parent: props.parentDoc?.name || 'new',
  parenttype: 'CRM Contract',
  parentfield: 'contract_items',
  ...props.item
})

watch(() => props.item, (newItem) => {
  localItem.value = {
    doctype: 'CRM Contract Item',
    parent: props.parentDoc?.name || 'new',
    parenttype: 'CRM Contract',
    parentfield: 'contract_items',
    ...newItem
  }
}, { deep: true, immediate: true })

const fields = computed(() => [
  {
    name: 'serial_no',
    label: 'Serial No',
    type: 'Link',
    options: 'Serial No',
    mandatory: true,
    fetch_from: 'serial_no.product_code',
    fetch_field: 'product_code'
  },
  {
    name: 'type',
    label: 'Type',
    type: 'Select',
    options: ['N/A', 'Warranty', 'AMC'],
    fetch_from: 'serial_no.type',
    fetch_field: 'type'
  },
  {
    name: 'warranty_start_date',
    label: 'Contract Start Date',
    type: 'Date',
    fetch_from: 'serial_no.warranty_start_date',
    fetch_field: 'warranty_start_date'
  },
  {
    name: 'warranty_expiry_date',
    label: 'Contract Expiry Date',
    type: 'Date'
  },
  {
    name: 'product_code',
    label: 'Product Code',
    type: 'Data',
    read_only: true
  },
  {
    name: 'product_name',
    label: 'Product Name',
    type: 'Data',
    read_only: true,
    fetch_from: 'serial_no.product_name',
    fetch_field: 'product_name'
  },
  {
    name: 'rate',
    label: 'Rate',
    type: 'Currency'
  },
  {
    name: 'amount',
    label: 'Amount',
    type: 'Currency',
    read_only: true
  }
])

async function handleFieldChange(fieldname, value) {
  // Create a new object to trigger reactivity
  const updatedItem = { ...localItem.value }
  updatedItem[fieldname] = value
  
  // Calculate amount when rate changes
  if (fieldname === 'rate') {
    updatedItem.amount = value || 0
  }
  
  // Fetch serial no details
  if (fieldname === 'serial_no' && value) {
    try {
      const response = await createResource({
        url: 'frappe.client.get',
        params: {
          doctype: 'Serial No',
          name: value,
          fields: ['product_code', 'product_name', 'type', 'warranty_start_date']
        },
        auto: true
      })
      
      if (response.data) {
        Object.assign(updatedItem, {
          product_code: response.data.product_code || '',
          product_name: response.data.product_name || '',
          type: response.data.type || 'N/A',
          warranty_start_date: response.data.warranty_start_date || ''
        })
      }
    } catch (error) {
      console.error('Error fetching serial no details:', error)
    }
  }
  
  // Update the local item after all changes
  localItem.value = updatedItem
}

function saveChanges() {
  const item = { ...localItem.value }
  emit('save', item)
  // Don't close the modal here, let the parent handle it
}

// Add watch for modelValue
watch(() => props.modelValue, (newValue) => {
  if (newValue) {
    nextTick(() => {
      localItem.value = {
        doctype: 'CRM Contract Item',
        parent: props.parentDoc?.name || 'new',
        parenttype: 'CRM Contract',
        parentfield: 'contract_items',
        ...props.item
      }
    })
  }
}, { immediate: true })
</script> 