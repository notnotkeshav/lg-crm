<template>
  <div class="space-y-4">
    <div class="flex justify-between items-center">
      <h3 class="text-base font-medium">{{ __('Contract Items') }}</h3>
      <Button variant="solid" @click="addItem">
        {{ __('Add Item') }}
      </Button>
    </div>

    <div class="overflow-x-auto">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th 
              v-for="col in columns" 
              :key="col.label" 
              class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider whitespace-nowrap"
              :style="{ width: col.width }"
            >
              {{ __(col.label) }}
              <span v-if="col.required" class="text-red-500">*</span>
            </th>
            <th class="w-20"></th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-for="(item, index) in modelValue" :key="index">
            <td 
              v-for="col in columns" 
              :key="col.fieldname" 
              class="px-4 py-2 whitespace-nowrap"
              :style="{ width: col.width }"
            >
              <template v-if="col.fieldtype === 'Link'">
                <Autocomplete
                  :placeholder="__('Select {0}', [col.label])"
                  :doctype="col.options"
                  v-model="item[col.fieldname]"
                  @change="(value) => handleFieldChange(index, col.fieldname, value)"
                  class="w-full"
                />
              </template>
              <template v-else-if="col.fieldtype === 'Select'">
                <FormControl
                  type="select"
                  :options="col.options.map(opt => ({ label: opt, value: opt }))"
                  v-model="item[col.fieldname]"
                  @change="(value) => handleFieldChange(index, col.fieldname, value)"
                  class="w-full"
                />
              </template>
              <template v-else>
                <FormControl
                  :type="col.fieldtype.toLowerCase()"
                  :read_only="col.read_only"
                  :required="col.required"
                  v-model="item[col.fieldname]"
                  @change="(value) => handleFieldChange(index, col.fieldname, value)"
                  class="w-full"
                />
              </template>
            </td>
            <td class="px-4 py-2 flex gap-2 whitespace-nowrap">
              <button
                class="text-blue-600 hover:text-blue-800"
                @click="editItem(item)"
              >
                <FeatherIcon name="edit-2" class="h-4 w-4" />
              </button>
              <button
                class="text-red-600 hover:text-red-800"
                @click="removeItem(index)"
              >
                <FeatherIcon name="trash-2" class="h-4 w-4" />
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Button, FormControl, FeatherIcon, Autocomplete } from 'frappe-ui'
import { createResource } from 'frappe-ui'

const props = defineProps({
  modelValue: {
    type: Array,
    default: () => []
  },
  parentDoc: {
    type: Object,
    default: () => ({
      doctype: 'CRM Contract',
      name: 'new'
    })
  }
})

const emit = defineEmits(['update:modelValue', 'edit-item'])

const columns = computed(() => [
  {
    label: 'Serial No',
    fieldname: 'serial_no',
    fieldtype: 'Link',
    options: 'Serial No',
    required: true,
    width: '200px'
  },
  {
    label: 'Type',
    fieldname: 'type',
    fieldtype: 'Select',
    options: ['N/A', 'Warranty', 'AMC'],
    width: '120px'
  },
  {
    label: 'Contract Start Date',
    fieldname: 'warranty_start_date',
    fieldtype: 'Date',
    width: '150px'
  },
  {
    label: 'Contract Expiry Date',
    fieldname: 'warranty_expiry_date',
    fieldtype: 'Date',
    width: '150px'
  },
  {
    label: 'Product Code',
    fieldname: 'product_code',
    fieldtype: 'Data',
    read_only: true,
    width: '150px'
  },
  {
    label: 'Product Name',
    fieldname: 'product_name',
    fieldtype: 'Data',
    read_only: true,
    width: '200px'
  },
  {
    label: 'Rate',
    fieldname: 'rate',
    fieldtype: 'Currency',
    width: '120px'
  },
  {
    label: 'Amount',
    fieldname: 'amount',
    fieldtype: 'Currency',
    read_only: true,
    width: '120px'
  }
])

function editItem(item) {
  emit('edit-item', { 
    ...item,
    doctype: 'CRM Contract Item',
    parent: props.parentDoc?.name || 'new',
    parenttype: 'CRM Contract',
    parentfield: 'contract_items'
  })
}

function removeItem(index) {
  const items = [...props.modelValue]
  items.splice(index, 1)
  // Reindex items
  items.forEach((item, idx) => {
    item.idx = idx + 1
  })
  emit('update:modelValue', items)
}

function addItem() {
  emit('edit-item', {
    doctype: 'CRM Contract Item',
    parent: props.parentDoc?.name || 'new',
    parenttype: 'CRM Contract',
    parentfield: 'contract_items',
    serial_no: '',
    type: 'N/A',
    warranty_start_date: '',
    warranty_expiry_date: '',
    product_code: '',
    product_name: '',
    rate: 0,
    amount: 0
  })
}

async function handleFieldChange(index, fieldname, value) {
  const items = [...props.modelValue]
  items[index][fieldname] = value
  
  // Calculate amount when rate changes
  if (fieldname === 'rate') {
    items[index].amount = value || 0
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
        items[index].product_code = response.data.product_code || ''
        items[index].product_name = response.data.product_name || ''
        items[index].type = response.data.type || 'N/A'
        items[index].warranty_start_date = response.data.warranty_start_date || ''
      }
    } catch (error) {
      console.error('Error fetching serial no details:', error)
    }
  }
  
  emit('update:modelValue', items)
}
</script> 