<template>
  <div class="flex flex-col h-full">
    <PageHeader :title="warranty.warranty_owner || warranty.name">
      <template #actions>
        <div class="flex items-center gap-2">
          <Button
            v-if="warranty.docstatus === 0"
            variant="solid"
            :label="__('Submit')"
            @click="submitWarranty"
          />
          <Button
            v-if="can_write"
            variant="solid"
            @click="openEditModal"
          >
            {{ __('Edit') }}
          </Button>
        </div>
      </template>
    </PageHeader>

    <div class="flex flex-1 min-h-0">
      <div class="flex-1 overflow-auto">
        <div class="p-4">
          <div class="grid grid-cols-3 gap-4">
            <InfoCard>
              <template #title>{{ __('Warranty Information') }}</template>
              <template #body>
                <div class="space-y-4">
                  <div>
                    <label class="text-sm text-gray-600">{{ __('Status') }}</label>
                    <div class="flex items-center gap-2">
                      <StatusDot :status="warranty.warranty_type" />
                      {{ warranty.warranty_type }}
                    </div>
                  </div>
                  <div>
                    <label class="text-sm text-gray-600">{{ __('Created On') }}</label>
                    <div>{{ formatDate(warranty.created_by) }}</div>
                  </div>
                  <div>
                    <label class="text-sm text-gray-600">{{ __('Expiry Date') }}</label>
                    <div>{{ formatDate(warranty.expiry_date) }}</div>
                  </div>
                  <div>
                    <label class="text-sm text-gray-600">{{ __('Requester') }}</label>
                    <div>{{ warranty.warranty_requester }}</div>
                  </div>
                </div>
              </template>
            </InfoCard>

            <InfoCard>
              <template #title>{{ __('Customer Information') }}</template>
              <template #body>
                <div class="space-y-4">
                  <div>
                    <label class="text-sm text-gray-600">{{ __('Customer') }}</label>
                    <div>{{ warranty.customer_name }}</div>
                  </div>
                  <div>
                    <label class="text-sm text-gray-600">{{ __('Organization') }}</label>
                    <div>
                      <router-link
                        v-if="warranty.organization"
                        :to="`/organization/${warranty.organization}`"
                        class="text-blue-600 hover:text-blue-800"
                      >
                        {{ warranty.organization }}
                      </router-link>
                    </div>
                  </div>
                  <div>
                    <label class="text-sm text-gray-600">{{ __('Phone') }}</label>
                    <div>{{ warranty.phone }}</div>
                  </div>
                  <div>
                    <label class="text-sm text-gray-600">{{ __('Email') }}</label>
                    <div>{{ warranty.email }}</div>
                  </div>
                </div>
              </template>
            </InfoCard>

            <InfoCard>
              <template #title>{{ __('Dealer Information') }}</template>
              <template #body>
                <div class="space-y-4">
                  <div>
                    <label class="text-sm text-gray-600">{{ __('Dealer Name') }}</label>
                    <div>{{ warranty.dealer_name }}</div>
                  </div>
                  <div>
                    <label class="text-sm text-gray-600">{{ __('Dealer ID') }}</label>
                    <div>{{ warranty.dealer_id }}</div>
                  </div>
                </div>
              </template>
            </InfoCard>
          </div>

          <Tabs class="mt-4">
            <Tab title="Activities">
              <Activities 
                :doctype="'Warranty'"
                :name="warranty.name"
                :counts="counts"
              />
            </Tab>
            <Tab title="Contacts">
              <ContactList 
                :contacts="warranty.contacts"
                :doctype="'Warranty'"
                :docname="warranty.name"
                @update="loadWarranty"
              />
            </Tab>
            <Tab title="Items">
              <ItemList
                :items="warranty.items"
                :doctype="'Warranty'"
                :docname="warranty.name"
                @update="loadWarranty"
              />
            </Tab>
            <Tab title="Files">
              <FileList 
                :doctype="'Warranty'"
                :name="warranty.name"
              />
            </Tab>
          </Tabs>
        </div>
      </div>

      <SidePanel
        :doctype="'Warranty'"
        :name="warranty.name"
        :fields="sidebarFields"
        @update="loadWarranty"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { createResource } from 'frappe-ui'
import { useRoute } from 'vue-router'
import { formatDate } from '@/utils'

const route = useRoute()
const warranty = ref({})
const counts = ref({})
const can_write = ref(false)
const sidebarFields = ref([])

const warrantyResource = createResource({
  url: 'crm.api.warranty.get_warranty',
  transform: (data) => data
})

const loadWarranty = async () => {
  warranty.value = await warrantyResource.submit({
    name: route.params.warrantyId
  })
  counts.value = {
    _email_count: warranty.value._email_count,
    _comment_count: warranty.value._comment_count,
    _task_count: warranty.value._task_count,
    _note_count: warranty.value._note_count,
  }
}

const submitWarranty = () => {
  createResource({
    url: 'crm.api.warranty.submit_warranty',
    params: { name: warranty.value.name },
    onSuccess() {
      loadWarranty()
    }
  })
}

onMounted(async () => {
  can_write.value = await frappe.db.has_permission('Warranty', 'write')
  loadWarranty()
})
</script>