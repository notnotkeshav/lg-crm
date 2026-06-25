<template>
  <Dialog v-model="show" :options="{ size: '3xl' }">
    <template #body>
      <div class="bg-white px-4 pb-6 pt-5 sm:px-6">
        <div class="mb-5 flex items-center justify-between">
          <div>
            <h3 class="text-2xl font-semibold leading-6 text-gray-900">
              {{ __('Create Warranty') }}
            </h3>
          </div>
          <div class="flex items-center gap-1">
            <Button
              variant="ghost"
              class="w-7"
              @click="show = false"
            >
              <FeatherIcon name="x" class="h-4 w-4" />
            </Button>
          </div>
        </div>

        <div class="space-y-4">
          <div v-if="error" class="text-red-600 text-sm">
            {{ error }}
          </div>

          <!-- Organization Section -->
          <div>
            <div class="flex items-center gap-3 text-sm text-gray-600 mb-4">
              <div>{{ __('Choose Existing Organization') }}</div>
              <Switch v-model="chooseExistingOrganization" />
            </div>

            <div v-if="chooseExistingOrganization">
              <Autocomplete
                v-model="warranty.organization"
                :label="__('Organization')"
                doctype="Organization"
                placeholder="Search organizations..."
                required
              />
            </div>
            <div v-else>
              <div class="grid grid-cols-2 gap-4">
                <Input
                  v-model="warranty.organization_name"
                  :label="__('Organization Name')"
                  required
                />
                <Input
                  v-model="warranty.organization_phone"
                  :label="__('Phone')"
                  type="tel"
                />
              </div>
            </div>
          </div>

          <!-- Customer Section -->
          <div>
            <div class="flex items-center gap-3 text-sm text-gray-600 mb-4">
              <div>{{ __('Choose Existing Customer') }}</div>
              <Switch v-model="chooseExistingCustomer" />
            </div>

            <div v-if="chooseExistingCustomer">
              <Autocomplete
                v-model="warranty.customer_id"
                :label="__('Customer')"
                doctype="Customer"
                placeholder="Search customers..."
                required
              />
            </div>
            <div v-else>
              <div class="grid grid-cols-2 gap-4">
                <Input
                  v-model="warranty.customer_name"
                  :label="__('Customer Name')"
                  required
                />
                <Input
                  v-model="warranty.email"
                  :label="__('Email')"
                  type="email"
                />
              </div>
            </div>
          </div>

          <!-- Warranty Details -->
          <div class="grid grid-cols-2 gap-4">
            <Input
              v-model="warranty.warranty_owner"
              :label="__('Warranty Owner')"
              required
            />
            <Select
              v-model="warranty.warranty_type"
              :label="__('Warranty Type')"
              :options="warrantyTypes"
              required
            />
          </div>

          <div class="grid grid-cols-2 gap-4">
            <Input
              v-model="warranty.warranty_requester"
              :label="__('Warranty Requester')"
            />
            <DatePicker
              v-model="warranty.expiry_date"
              :label="__('Expiry Date')"
              required
            />
          </div>

          <!-- Dealer Information -->
          <div class="grid grid-cols-2 gap-4">
            <Input
              v-model="warranty.dealer_name"
              :label="__('Dealer Name')"
            />
            <Input
              v-model="warranty.dealer_id"
              :label="__('Dealer ID')"
            />
          </div>

          <!-- Notes -->
          <div>
            <Textarea
              v-model="warranty.notes"
              :label="__('Notes')"
              :placeholder="__('Add any additional notes...')"
              rows="3"
            />
          </div>
        </div>

        <div class="mt-6 flex justify-end gap-2">
          <Button
            variant="secondary"
            :label="__('Cancel')"
            @click="show = false"
          />
          <Button
            variant="solid"
            :label="__('Create')"
            :loading="isCreating"
            @click="createWarranty"
          />
        </div>
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { createResource } from 'frappe-ui'
import { useRouter } from 'vue-router'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  defaults: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['update:modelValue', 'created'])
const router = useRouter()

const show = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const warrantyTypes = [
  { label: 'Standard', value: 'Standard' },
  { label: 'Extended', value: 'Extended' },
  { label: 'Premium', value: 'Premium' }
]

const chooseExistingOrganization = ref(false)
const chooseExistingCustomer = ref(false)
const isCreating = ref(false)
const error = ref(null)

const warranty = ref({
  warranty_owner: '',
  warranty_type: '',
  warranty_requester: '',
  expiry_date: '',
  customer_name: '',
  customer_id: '',
  organization: '',
  organization_name: '',
  organization_phone: '',
  dealer_name: '',
  dealer_id: '',
  email: '',
  notes: ''
})

const createWarranty = () => {
  isCreating.value = true
  error.value = null

  createResource({
    url: 'lg.api.warranty.create_warranty',
    params: {
      args: {
        ...warranty.value,
        choose_existing_organization: chooseExistingOrganization.value,
        choose_existing_customer: chooseExistingCustomer.value
      }
    },
    onSuccess(data) {
      isCreating.value = false
      show.value = false
      emit('created', data)
      router.push({ name: 'Warranty', params: { warrantyId: data.name } })
    },
    onError(err) {
      isCreating.value = false
      error.value = err.message
    }
  })
}

// Watch customer_id to fetch customer name
watch(() => warranty.value.customer_id, async (newValue) => {
  if (newValue) {
    const customer = await frappe.db.get_doc('Customer', newValue)
    warranty.value.customer_name = customer.customer_name
    warranty.value.email = customer.email_id
  }
})

// Watch organization to fetch organization details
watch(() => warranty.value.organization, async (newValue) => {
  if (newValue) {
    const organization = await frappe.db.get_doc('Organization', newValue)
    warranty.value.organization_name = organization.organization_name
    warranty.value.organization_phone = organization.phone
  }
})

// Initialize with defaults
watch(() => props.defaults, (newDefaults) => {
  Object.assign(warranty.value, newDefaults)
}, { immediate: true })
</script>