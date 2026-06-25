<template>
  <LayoutHeader v-if="contract.data">
    <template #left-header>
      <Breadcrumbs :items="breadcrumbs">
        <template #prefix="{ item }">
          <Icon v-if="item.icon" :icon="item.icon" class="mr-2 h-4" />
        </template>
      </Breadcrumbs>
    </template>
    <template #right-header>
      <CustomActions v-if="customActions" :actions="customActions" />
      <component :is="contract.data._assignedTo?.length == 1 ? 'Button' : 'div'">
        <MultipleAvatar
          :avatars="contract.data._assignedTo"
          @click="showAssignmentModal = true"
        />
      </component>
    </template>
  </LayoutHeader>
  <div v-if="contract.data" class="flex h-full overflow-hidden">
    <div class="flex flex-1 flex-col overflow-hidden">
      <Tabs v-model="tabIndex" :tabs="tabs" class="flex-1">
        <Activities
          ref="activities"
          doctype="CRM Contract"
          :tabs="tabs"
          v-model:reload="reload"
          v-model:tabIndex="tabIndex"
          v-model="contract"
          @email-sent="handleEmailSent"
          @comment-added="handleCommentAdded"
        />
      </Tabs>
    </div>
    <Resizer side="right" class="flex w-[400px] min-w-[400px] flex-col justify-between border-l">
      <div
        class="flex h-10.5 cursor-copy items-center justify-between border-b px-5 py-2.5"
      >
        <div class="flex items-center">
          <span class="text-lg font-medium" @click="copyToClipboard(contract.data.name)">
            {{ __(contract.data.name) }}
          </span>
        </div>
        <div class="flex items-center gap-2">
          <Badge
            v-if="contract.data.deal_type"
            :label="contract.data.deal_type"
            variant="subtle"
            theme="blue"
          />
          <Badge
            v-if="contract.data.amount"
            :label="formatCurrency(contract.data.amount, contract.data.currency)"
            variant="subtle"
            theme="green"
          />
          <Badge
            v-if="contract.data.expiry_date"
            :label="formatDate(contract.data.expiry_date)"
            variant="subtle"
            :theme="isExpired ? 'red' : 'gray'"
          />
        </div>
      </div>
      <div class="flex items-center justify-start gap-5 border-b p-5">
        <Tooltip :text="__('Organization logo')">
          <div class="group relative size-12">
            <Avatar
              size="3xl"
              class="size-12"
              :label="organization.data?.name || __('Untitled')"
              :image="organization.data?.organization_logo"
            />
          </div>
        </Tooltip>
        <div class="flex flex-col gap-2.5 truncate">
          <Tooltip :text="organization.data?.name || __('Set a customer')">
            <div class="truncate text-2xl font-medium">
              {{ organization.data?.name || __('Untitled') }}
            </div>
          </Tooltip>
          <div class="flex gap-1.5">
            <Tooltip v-if="callEnabled" :text="__('Make a call')">
              <Button class="h-7 w-7" @click="triggerCall">
                <PhoneIcon class="h-4 w-4" />
              </Button>
            </Tooltip>
            <Tooltip :text="__('Send an email')">
              <Button class="h-7 w-7" @click="openEmailBox">
                <Email2Icon
                  class="h-4 w-4"
                  @click="
                    contract.data.email
                      ? openEmailBox()
                      : errorMessage(__('No email set'))
                  "
                />
              </Button>
            </Tooltip>
            <Tooltip :text="__('Go to website')">
              <Button class="h-7 w-7">
                <LinkIcon
                  class="h-4 w-4"
                  @click="
                    contract.data.website
                      ? openWebsite(contract.data.website)
                      : errorMessage(__('No website set'))
                  "
                />
              </Button>
            </Tooltip>
          </div>
        </div>
      </div>
      <div
        v-if="fieldsLayout.data"
        class="flex flex-1 flex-col justify-between overflow-hidden"
      >
        <div class="flex flex-col overflow-y-auto">
          <div class="flex items-center justify-between border-b p-3">
            <div class="text-base font-medium">{{ __('Details') }}</div>
            <div class="flex items-center gap-2">
              <Tooltip :text="__('Attach a file')">
                <Button class="size-7" @click="showFilesUploader = true">
                  <AttachmentIcon class="size-4" />
                </Button>
              </Tooltip>
              <Button
                v-if="isManager()"
                variant="ghost"
                class="w-7"
                @click="handleLayoutEdit"
              >
                <EditIcon class="h-4 w-4" />
              </Button>
            </div>
          </div>
          <div
            v-for="(section, i) in fieldsLayout.data"
            :key="section.label"
            class="section flex flex-col p-3"
            :class="{ 'border-b': i !== fieldsLayout.data.length - 1 }"
          >
            <Section :is-opened="section.opened" :label="section.label">
              <SectionFields
                v-if="section.fields"
                :fields="section.fields"
                :isLastSection="i == fieldsLayout.data.length - 1"
                v-model="contract.data"
                @update="(field, value) => handleFieldChange(field, value)"
              />
            </Section>
          </div>
        </div>
      </div>
    </Resizer>
  </div>
  <OrganizationModal
    v-model="showOrganizationModal"
    v-model:organization="_organization"
    :options="{
      redirect: false,
      afterInsert: (doc) => updateField('customer', doc.name),
    }"
  />
  <ContactModal
    v-model="showContactModal"
    :contact="_contact"
    :options="{
      redirect: false,
      afterInsert: (doc) => addContact(doc.name),
    }"
  />
  <AssignmentModal
    v-if="showAssignmentModal"
    v-model="showAssignmentModal"
    v-model:assignees="contract.data._assignedTo"
    :doc="contract.data"
    doctype="CRM Contract"
  />
  <SidePanelModal
    v-if="showSidePanelModal"
    v-model="showSidePanelModal"
    doctype="CRM Contract"
    @reload="() => fieldsLayout.reload()"
  />
  <FilesUploader
    v-if="contract.data?.name"
    v-model="showFilesUploader"
    doctype="CRM Contract"
    :docname="contract.data.name"
    @after="
      () => {
        activities?.all_activities?.reload()
        changeTabTo('attachments')
      }
    "
  />
</template>

<script setup>
import Icon from '@/components/Icon.vue'
import Resizer from '@/components/Resizer.vue'
import LoadingIndicator from '@/components/Icons/LoadingIndicator.vue'
import EditIcon from '@/components/Icons/EditIcon.vue'
import ActivityIcon from '@/components/Icons/ActivityIcon.vue'
import EmailIcon from '@/components/Icons/EmailIcon.vue'
import Email2Icon from '@/components/Icons/Email2Icon.vue'
import CommentIcon from '@/components/Icons/CommentIcon.vue'
import PhoneIcon from '@/components/Icons/PhoneIcon.vue'
import TaskIcon from '@/components/Icons/TaskIcon.vue'
import NoteIcon from '@/components/Icons/NoteIcon.vue'
import WhatsAppIcon from '@/components/Icons/WhatsAppIcon.vue'
import IndicatorIcon from '@/components/Icons/IndicatorIcon.vue'
import LinkIcon from '@/components/Icons/LinkIcon.vue'
import ArrowUpRightIcon from '@/components/Icons/ArrowUpRightIcon.vue'
import SuccessIcon from '@/components/Icons/SuccessIcon.vue'
import AttachmentIcon from '@/components/Icons/AttachmentIcon.vue'
import LayoutHeader from '@/components/LayoutHeader.vue'
import Activities from '@/components/Activities/Activities.vue'
import OrganizationModal from '@/components/Modals/OrganizationModal.vue'
import AssignmentModal from '@/components/Modals/AssignmentModal.vue'
import FilesUploader from '@/components/FilesUploader/FilesUploader.vue'
import MultipleAvatar from '@/components/MultipleAvatar.vue'
import ContactModal from '@/components/Modals/ContactModal.vue'
import SidePanelModal from '@/components/Settings/SidePanelModal.vue'
import Link from '@/components/Controls/Link.vue'
import Section from '@/components/Section.vue'
import SectionFields from '@/components/SectionFields.vue'
import SLASection from '@/components/SLASection.vue'
import CustomActions from '@/components/CustomActions.vue'
import {
  openWebsite,
  createToast,
  setupAssignees,
  setupCustomizations,
  errorMessage,
  copyToClipboard,
} from '@/utils'
import { formatCurrency, formatDate } from '@/utils/format'
import { getView } from '@/utils/view'
import { globalStore } from '@/stores/global'
import { usersStore } from '@/stores/users'
import { whatsappEnabled, callEnabled } from '@/composables/settings'
import {
  createResource,
  Dropdown,
  Tooltip,
  Avatar,
  Tabs,
  Breadcrumbs,
  call,
  usePageMeta,
} from 'frappe-ui'
import { ref, computed, h, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useActiveTabManager } from '@/composables/useActiveTabManager'

const { $dialog, $socket, makeCall } = globalStore()
const { isManager } = usersStore()
const route = useRoute()
const router = useRouter()

const props = defineProps({
  contractId: {
    type: String,
    required: true,
  },
})

const customActions = ref([])
const customStatuses = ref([])
const showContactModal = ref(false)
const _contact = ref({})
const _organization = ref({})
const showOrganizationModal = ref(false)

const contract = createResource({
  url: 'lg.lg.doctype.crm_contract.api.get_contract',
  params: { name: props.contractId },
  cache: ['contract', props.contractId],
  onSuccess: async (data) => {
    if (data.customer) {
      organization.update({
        params: { doctype: 'CRM Organization', name: data.customer },
      })
      organization.fetch()
    }

    let obj = {
      doc: data,
      $dialog,
      $socket,
      router,
      updateField,
      createToast,
      deleteDoc: deleteContract,
      resource: {
        contract,
        contractContacts,
        fieldsLayout,
      },
      call,
    }
    setupAssignees(data)
    let customization = await setupCustomizations(data, obj)
    customActions.value = customization.actions || []
  },
})

const organization = createResource({
  url: 'frappe.client.get_value',
  params: {
    doctype: 'CRM Organization',
    filters: { name: contract.data?.customer },
    fieldname: ['name', 'organization_logo']
  },
  onSuccess: (data) => (contract.data._organizationObj = data),
})

onMounted(() => {
  $socket.on('crm_customer_created', () => {
    createToast({
      title: __('Customer created successfully'),
      icon: 'check',
      iconClasses: 'text-green-600',
    })
  })

  if (contract.data) {
    organization.data = contract.data._organizationObj
    return
  }
  contract.fetch()
})

onBeforeUnmount(() => {
  $socket.off('crm_customer_created')
})

const reload = ref(false)
const showAssignmentModal = ref(false)
const showSidePanelModal = ref(false)
const showFilesUploader = ref(false)

function updateContract(fieldname, value, callback) {
  value = Array.isArray(fieldname) ? '' : value

  if (validateRequired(fieldname, value)) return

  createResource({
    url: 'frappe.client.set_value',
    params: {
      doctype: 'CRM Contract',
      name: props.contractId,
      fieldname,
      value,
    },
    auto: true,
    onSuccess: () => {
      contract.reload()
      reload.value = true
      createToast({
        title: __('Contract updated'),
        icon: 'check',
        iconClasses: 'text-green-600',
      })
      callback?.()
    },
    onError: (err) => {
      createToast({
        title: __('Error updating contract'),
        text: __(err.messages?.[0]),
        icon: 'x',
        iconClasses: 'text-red-600',
      })
    },
  })
}

function validateRequired(fieldname, value) {
  let meta = contract.data.fields_meta || {}
  if (meta[fieldname]?.reqd && !value) {
    createToast({
      title: __('Error Updating Contract'),
      text: __('{0} is a required field', [meta[fieldname].label]),
      icon: 'x',
      iconClasses: 'text-red-600',
    })
    return true
  }
  return false
}

const breadcrumbs = computed(() => {
  let items = [{ label: __('Contracts'), route: { name: 'Contracts' } }]

  if (route.query.view || route.query.viewType) {
    let view = getView(route.query.view, route.query.viewType, 'CRM Contract')
    if (view) {
      items.push({
        label: __(view.label),
        icon: view.icon,
        route: {
          name: 'Contracts',
          params: { viewType: route.query.viewType },
          query: { view: route.query.view },
        },
      })
    }
  }

  items.push({
    label: organization.data?.name || __('Untitled'),
    route: { name: 'Contract', params: { contractId: contract.data.name } },
  })
  return items
})

usePageMeta(() => {
  return {
    title: organization.data?.name || contract.data?.name,
  }
})

const activities = ref(null)

function openEmailBox() {
  if (!contract.data.email) {
    errorMessage(__('No email set'))
    return
  }
  
  tabIndex.value = tabs.value.findIndex(tab => tab.name === 'Emails')
  nextTick(() => {
    if (activities.value && activities.value.emailBox) {
      activities.value.emailBox.show = true
    }
  })
}

function handleEmailSent() {
  createToast({
    title: __('Email sent successfully'),
    icon: 'check',
    iconClasses: 'text-green-600',
  })
  activities.value?.all_activities?.reload()
}

function handleCommentAdded() {
  createToast({
    title: __('Comment added successfully'),
    icon: 'check',
    iconClasses: 'text-green-600',
  })
  activities.value?.all_activities?.reload()
}

function changeTabTo(tabName) {
  const index = tabs.value.findIndex((tab) => tab.name.toLowerCase() === tabName.toLowerCase())
  if (index !== -1) {
    tabIndex.value = index
  }
}

const tabs = computed(() => {
  let tabOptions = [
    {
      name: 'Activity',
      label: __('Activity'),
      icon: ActivityIcon,
    },
    {
      name: 'Emails',
      label: __('Emails'),
      icon: EmailIcon,
    },
    {
      name: 'Comments',
      label: __('Comments'),
      icon: CommentIcon,
    },
    {
      name: 'Tasks',
      label: __('Tasks'),
      icon: TaskIcon,
    },
    {
      name: 'Notes',
      label: __('Notes'),
      icon: NoteIcon,
    },
    {
      name: 'Attachments',
      label: __('Attachments'),
      icon: AttachmentIcon,
    },
  ]
  return tabOptions.filter((tab) => (tab.condition ? tab.condition() : true))
})

const { tabIndex } = useActiveTabManager(tabs, 'lastContractTab')

const isExpired = computed(() => {
  if (!contract.data?.expiry_date) return false
  return new Date(contract.data.expiry_date) < new Date()
})

const defaultFields = [
  {
    name: 'Contract Details',
    fields: [
      { fieldname: 'customer', label: 'Customer', required: true },
      { fieldname: 'date', label: 'Date', required: true },
      { fieldname: 'contract_from', label: 'Contract From' },
      { fieldname: 'deal_type', label: 'Contract Type' },
      { fieldname: 'serial_no', label: 'Serial No.' },
      { fieldname: 'product_name', label: 'Product Name' },
      { fieldname: 'start_date', label: 'Start Date' },
      { fieldname: 'expiry_date', label: 'Expiry Date' },
    ]
  },
  {
    name: 'AMC Details',
    fields: [
      { fieldname: 'amc', label: 'AMC Price List' },
      { fieldname: 'amount', label: 'Amount' },
      { fieldname: 'currency', label: 'Currency', required: true },
      { fieldname: 'payment_frequency', label: 'Payment Frequency' },
    ]
  },
  {
    name: 'Address & Contacts',
    fields: [
      { fieldname: 'customer_address', label: 'Customer Address' },
      { fieldname: 'shipping_address', label: 'Shipping Address' },
    ]
  }
]

const fieldsLayout = createResource({
  url: 'crm.api.doc.get_sidebar_fields',
  cache: ['fieldsLayout', props.contractId],
  params: { 
    doctype: 'CRM Contract', 
    name: props.contractId,
    default_fields: defaultFields 
  },
  auto: true,
  transform: (data) => getParsedFields(data),
})

function getParsedFields(sections) {
  sections.forEach((section) => {
    if (section.name == 'contacts_section') return
    section.fields.forEach((field) => {
      if (field.name == 'customer') {
        field.create = (value, close) => {
          _organization.value.organization_name = value
          showOrganizationModal.value = true
          close()
        }
        field.link = (org) =>
          router.push({
            name: 'Organization',
            params: { organizationId: org },
          })
      }
    })
  })
  return sections
}

function contactOptions(contact) {
  let options = [
    {
      label: __('Remove'),
      icon: 'trash-2',
      onClick: () => removeContact(contact.name),
    },
  ]

  if (!contact.is_primary) {
    options.push({
      label: __('Set as Primary Contact'),
      icon: h(SuccessIcon, { class: 'h-4 w-4' }),
      onClick: () => setPrimaryContact(contact.name),
    })
  }

  return options
}

async function addContact(contact) {
  let d = await call('lg.lg.doctype.crm_contract.api.add_contact', {
    contract: props.contractId,
    contact,
  })
  if (d) {
    contractContacts.reload()
    createToast({
      title: __('Contact added'),
      icon: 'check',
      iconClasses: 'text-green-600',
    })
  }
}

async function removeContact(contact) {
  let d = await call('lg.lg.doctype.crm_contract.api.remove_contact', {
    contract: props.contractId,
    contact,
  })
  if (d) {
    contractContacts.reload()
    createToast({
      title: __('Contact removed'),
      icon: 'check',
      iconClasses: 'text-green-600',
    })
  }
}

async function setPrimaryContact(contact) {
  let d = await call('lg.lg.doctype.crm_contract.api.set_primary_contact', {
    contract: props.contractId,
    contact,
  })
  if (d) {
    contractContacts.reload()
    createToast({
      title: __('Primary contact set'),
      icon: 'check',
      iconClasses: 'text-green-600',
    })
  }
}

const contractContacts = createResource({
  url: 'lg.lg.doctype.crm_contract.api.get_contract_contacts',
  params: { name: props.contractId },
  cache: ['contract_contacts', props.contractId],
  auto: true,
  transform: (data) => {
    data.forEach((contact) => {
      contact.opened = false
    })
    return data
  },
})

function triggerCall() {
  let primaryContact = contractContacts.data?.find((c) => c.is_primary)
  let mobile_no = primaryContact?.mobile_no || null

  if (!primaryContact) {
    errorMessage(__('No primary contact set'))
    return
  }

  if (!mobile_no) {
    errorMessage(__('No mobile number set'))
    return
  }

  makeCall(mobile_no)
}

function updateField(name, value, callback) {
  updateContract(name, value, () => {
    contract.data[name] = value
    callback?.()
  })
}

async function deleteContract(name) {
  await call('frappe.client.delete', {
    doctype: 'CRM Contract',
    name,
  })
  router.push({ name: 'Contracts' })
}

function handleLayoutEdit() {
  showSidePanelModal.value = true
}

function handleFieldChange(field, value) {
  if (field.required && !value) {
    createToast({
      title: __('Error'),
      text: __('{0} is required', [field.label]),
      icon: 'x',
      iconClasses: 'text-red-600',
    })
    return false
  }
  
  updateField(field.fieldname, value)
  return true
}
</script>

<style scoped>
:deep(.section:has(.section-field.hidden)) {
  display: none;
}
:deep(.section:has(.section-field:not(.hidden))) {
  display: flex;
}
</style>