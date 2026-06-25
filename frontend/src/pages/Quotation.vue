<template>
<LayoutHeader v-if="quotation.data">
    <template #left-header>
      <Breadcrumbs :items="breadcrumbs">
        <template #prefix="{ item }">
          <Icon v-if="item.icon" :icon="item.icon" class="mr-2 h-4" />
        </template>
      </Breadcrumbs>
    </template>
    <template #right-header>
      <CustomActions v-if="customActions" :actions="customActions" />
      <component :is="quotation.data._assignedTo?.length == 1 ? 'Button' : 'div'">
        <MultipleAvatar
          :avatars="quotation.data._assignedTo"
          @click="showAssignmentModal = true"
        />
      </component>
      <Dropdown :options="quotationStatusOptions">
        <template #default="{ open }">
          <Button
            :label="quotation.data.status"
            :class="getStatusColorClass(quotation.data._status_doc?.color)"
          >
            <template #prefix>
              <IndicatorIcon />
            </template>
            <template #suffix>
              <FeatherIcon
                :name="open ? 'chevron-up' : 'chevron-down'"
                class="h-4"
              />
            </template>
          </Button>
        </template>
      </Dropdown>
    </template>
  </LayoutHeader>

  <!-- Add KPI Cards Section -->
  <div v-if="quotation.data && showKPICards" class="bg-white px-4 py-5 shadow sm:rounded-lg sm:p-6">
    <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 md:grid-cols-4">
      <!-- Amount Card -->
      <div class="rounded-lg border border-gray-200 bg-gray-50 p-4">
        <dt class="text-sm font-medium text-gray-500">{{ __('Total Amount') }}</dt>
        <dd class="mt-1 flex items-baseline justify-between md:block lg:flex">
          <div class="flex items-baseline text-2xl font-semibold text-primary-600">
            {{ formatAmount(quotation.data.amount, quotation.data.currency) }}
          </div>
        </dd>
      </div>

      <!-- Status Card -->
      <div class="rounded-lg border border-gray-200 bg-gray-50 p-4">
        <dt class="text-sm font-medium text-gray-500">{{ __('Status') }}</dt>
        <dd class="mt-1">
          <Badge
            :variant="getQuotationStatusDetails(quotation.data._status_doc).variant"
            :theme="getQuotationStatusDetails(quotation.data._status_doc).theme"
          >
            {{ quotation.data.status }}
          </Badge>
        </dd>
      </div>

      <!-- Valid Till Card -->
      <div class="rounded-lg border border-gray-200 bg-gray-50 p-4">
        <dt class="text-sm font-medium text-gray-500">{{ __('Valid Till') }}</dt>
        <dd class="mt-1 flex items-baseline justify-between md:block lg:flex">
          <div class="flex items-baseline text-2xl font-semibold text-gray-900">
            {{ formatDate(quotation.data.valid_till) }}
          </div>
          <div v-if="isExpiringSoon" class="text-sm text-yellow-600">
            {{ __('Expiring soon (Within two months)') }}
          </div>
        </dd>
      </div>

      <!-- Deal Type Card -->
      <div class="rounded-lg border border-gray-200 bg-gray-50 p-4">
        <dt class="text-sm font-medium text-gray-500">{{ __('Deal Type') }}</dt>
        <dd class="mt-1 flex items-baseline justify-between md:block lg:flex">
          <div class="flex items-baseline text-2xl font-semibold text-gray-900">
            {{ quotation.data.deal_type }}
          </div>
        </dd>
      </div>
    </div>
  </div>

  <div v-if="quotation.data" class="flex h-full overflow-hidden">
    <Tabs as="div" v-model="tabIndex" :tabs="tabs">
      <template #tab-panel>
        <template v-if="tabs[tabIndex].name === 'Data'">
          <div class="flex flex-col overflow-y-auto">
            <div
              v-for="(section, i) in fieldsLayout.data"
              :key="section.label"
              class="section flex flex-col p-3"
              :class="{ 'border-b': i !== fieldsLayout.data.length - 1 }"
            >
              <Section :is-opened="section.opened" :label="section.label">
                <template #actions>
                  <Button
                    v-if="((!section.contacts && i == 1) || i == 0) && isManager()"
                    variant="ghost"
                    class="w-7 mr-2"
                    @click="showSidePanelModal = true"
                  >
                    <EditIcon class="h-4 w-4" />
                  </Button>
                </template>
                <SectionFields
                  v-if="section.fields"
                  :fields="section.fields"
                  :isLastSection="i == fieldsLayout.data.length - 1"
                  v-model="quotation.data"
                  @update="updateField"
                />
              </Section>
            </div>
          </div>
        </template>
        <template v-else-if="tabs[tabIndex].name === 'Attachments'">
          <div class="p-4">
            <AttachmentArea
              :attachments="attachments.data"
              @reload="attachments.reload"
              @add="showFilesUploader = true"
            />
          </div>
        </template>
        <Activities
          v-else
          ref="activities"
          doctype="CRM Quotation"
          :tabs="tabs"
          v-model:reload="reload"
          v-model:tabIndex="tabIndex"
          v-model="quotation"
          @email-sent="handleEmailSent"
          @comment-added="handleCommentAdded"
        />
      </template>
    </Tabs>
    <Resizer side="right" class="flex w-[400px] min-w-[400px] flex-col justify-between border-l">
      <div
        class="flex h-10.5 cursor-copy items-center border-b px-5 py-2.5 text-lg font-medium"
        @click="copyToClipboard(quotation.data.name)"
      >
        {{ __(quotation.data.name) }}
      </div>
      <div class="flex items-center justify-start gap-5 border-b p-5">
        <Tooltip :text="__('Customer logo')">
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
              <Button class="h-7 w-7">
                <Email2Icon
                  class="h-4 w-4"
                  @click="
                    quotation.data.email
                      ? openEmailBox()
                      : errorMessage(__('No email set'))
                  "
                />
              </Button>
            </Tooltip>
            <Tooltip :text="__('Attach a file')">
              <Button class="size-7" @click="showFilesUploader = true">
                <AttachmentIcon class="size-4" />
              </Button>
            </Tooltip>
          </div>
        </div>
      </div>
      <SLASection
        v-if="quotation.data.sla_status"
        v-model="quotation.data"
        @updateField="updateField"
      />
      <div
        v-if="fieldsLayout.data"
        class="flex flex-1 flex-col justify-between overflow-hidden"
      >
        <div class="flex flex-col overflow-y-auto">
          <div
            v-for="(section, i) in fieldsLayout.data"
            :key="section.label"
            class="section flex flex-col p-3"
            :class="{ 'border-b': i !== fieldsLayout.data.length - 1 }"
          >
            <Section :is-opened="section.opened" :label="section.label">
              <template #actions>
                <div v-if="section.contacts" class="pr-2">
                  <Link
                    value=""
                    doctype="Contact"
                    @change="(e) => addContact(e)"
                    :onCreate="
                      (value, close) => {
                        _contact = {
                          first_name: value,
                          company_name: quotation.data.customer,
                        }
                        showContactModal = true
                        close()
                      }
                    "
                  >
                    <template #target="{ togglePopover }">
                      <Button
                        class="h-7 px-3"
                        variant="ghost"
                        icon="plus"
                        @click="togglePopover()"
                      />
                    </template>
                  </Link>
                </div>
                <Button
                  v-else-if="
                    ((!section.contacts && i == 1) || i == 0) && isManager()
                  "
                  variant="ghost"
                  class="w-7 mr-2"
                  @click="showSidePanelModal = true"
                >
                  <EditIcon class="h-4 w-4" />
                </Button>
              </template>
              <SectionFields
                v-if="section.fields"
                :fields="section.fields"
                :isLastSection="i == fieldsLayout.data.length - 1"
                v-model="quotation.data"
                @update="updateField"
              />
              <div v-else>
                <div
                  v-if="
                    quotationContacts?.loading && quotationContacts?.data?.length == 0
                  "
                  class="flex min-h-20 flex-1 items-center justify-center gap-3 text-base text-gray-500"
                >
                  <LoadingIndicator class="h-4 w-4" />
                  <span>{{ __('Loading...') }}</span>
                </div>
                <div
                  v-else-if="quotationContacts?.data?.length"
                  v-for="(contact, i) in quotationContacts.data"
                  :key="contact.name"
                >
                  <div
                    class="px-2 pb-2.5"
                    :class="[i == 0 ? 'pt-5' : 'pt-2.5']"
                  >
                    <Section :is-opened="contact.opened">
                      <template #header="{ opened, toggle }">
                        <div
                          class="flex cursor-pointer items-center justify-between gap-2 pr-1 text-base leading-5 text-gray-700"
                        >
                          <div
                            class="flex h-7 items-center gap-2 truncate"
                            @click="toggle()"
                          >
                            <Avatar
                              :label="contact.full_name"
                              :image="contact.image"
                              size="md"
                            />
                            <div class="truncate">
                              {{ contact.full_name }}
                            </div>
                            <Badge
                              v-if="contact.is_primary"
                              class="ml-2"
                              variant="outline"
                              :label="__('Primary')"
                              theme="green"
                            />
                          </div>
                          <div class="flex items-center">
                            <Dropdown :options="contactOptions(contact)">
                              <Button
                                icon="more-horizontal"
                                class="text-gray-600"
                                variant="ghost"
                              />
                            </Dropdown>
                            <Button
                              variant="ghost"
                              @click="
                                router.push({
                                  name: 'Contact',
                                  params: { contactId: contact.name },
                                })
                              "
                            >
                              <ArrowUpRightIcon class="h-4 w-4" />
                            </Button>
                            <Button variant="ghost" @click="toggle()">
                              <FeatherIcon
                                name="chevron-right"
                                class="h-4 w-4 text-gray-900 transition-all duration-300 ease-in-out"
                                :class="{ 'rotate-90': opened }"
                              />
                            </Button>
                          </div>
                        </div>
                      </template>
                      <div
                        class="flex flex-col gap-1.5 text-base text-gray-800"
                      >
                        <div class="flex items-center gap-3 pb-1.5 pl-1 pt-4">
                          <Email2Icon class="h-4 w-4" />
                          {{ contact.email }}
                        </div>
                        <div class="flex items-center gap-3 p-1 py-1.5">
                          <PhoneIcon class="h-4 w-4" />
                          {{ contact.mobile_no }}
                        </div>
                      </div>
                    </Section>
                  </div>
                  <div
                    v-if="i != quotationContacts.data.length - 1"
                    class="mx-2 h-px border-t border-gray-200"
                  />
                </div>
                <div
                  v-else
                  class="flex h-20 items-center justify-center text-base text-gray-600"
                >
                  {{ __('No contacts added') }}
                </div>
              </div>
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
    v-model:assignees="quotation.data._assignedTo"
    :doc="quotation.data"
    doctype="CRM Quotation"
  />
  <SidePanelModal
    v-if="showSidePanelModal"
    v-model="showSidePanelModal"
    doctype="CRM Quotation"
    @reload="() => fieldsLayout.reload()"
  />
  <FilesUploader
    v-if="quotation.data?.name"
    v-model="showFilesUploader"
    doctype="CRM Quotation"
    :docname="quotation.data.name"
    @after="
      () => {
        activities?.all_activities?.reload()
        attachments.reload()
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
import DetailsIcon from '@/components/Icons/DetailsIcon.vue'
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
import { statusesStore } from '@/stores/statuses'
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
import { ref, computed, h, onMounted, onBeforeUnmount, nextTick, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useActiveTabManager } from '@/composables/useActiveTabManager'
import AttachmentArea from '@/components/AttachmentPreview/AttachmentArea.vue'

const props = defineProps({
  quotationId: {
    type: String,
    required: true,
  },
})

const { $dialog, $socket, makeCall } = globalStore()
const { getQuotationStatus } = statusesStore()
const { isManager } = usersStore()
const route = useRoute()
const router = useRouter()

const customActions = ref([])
const customStatuses = ref([])

const quotation = createResource({
  url: 'lg.lg.doctype.crm_quotation.api.get_quotation',
  params: { name: props.quotationId },
  cache: ['quotation', props.quotationId],
  onError: (error) => {
    createToast({
      title: __('Error loading quotation'),
      text: error.message,
      icon: 'x',
      iconClasses: 'text-red-600',
    })
    router.push({ name: 'Quotations' })
  },
  onSuccess: async (data) => {
    if (!data) {
      createToast({
        title: __('Error'),
        text: __('Quotation not found'),
        icon: 'x',
        iconClasses: 'text-red-600',
      })
      router.push({ name: 'Quotations' })
      return
    }

    // Fetch status details if status is set
    if (data.status) {
      try {
        const statusDoc = await call('frappe.client.get', {
          doctype: 'CRM Quotation Status',
          name: data.status
        })
        data._status_doc = statusDoc
      } catch (error) {
        console.error('Error fetching status details:', error)
      }
    }

    if (data.customer) {
      organization.update({
        params: {
          doctype: 'CRM Organization',
          name: data.customer,
          fieldname: ['name', 'organization_logo', 'organization_name']
        },
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
      deleteDoc: deleteQuotation,
      resource: {
        quotation,
        quotationContacts,
        fieldsLayout,
      },
      call,
    }
    setupAssignees(data)
    let customization = await setupCustomizations(data, obj)
    customActions.value = customization.actions || []
    customStatuses.value = customization.statuses || []
  },
})

const organization = createResource({
  url: 'frappe.client.get',
  params: {
    doctype: 'CRM Organization',
    filters: { name: quotation.data?.customer },
    fieldname: ['name', 'organization_logo', 'organization_name']
  },
  onError: (error) => {
    createToast({
      title: __('Error loading organization'),
      text: error.message,
      icon: 'x',
      iconClasses: 'text-red-600',
    })
  },
  onSuccess: (data) => {
    if (data?.message) {
      quotation.data._organizationObj = data.message
    }
  },
})

onMounted(() => {
  $socket.on('crm_customer_created', () => {
    createToast({
      title: __('Customer created successfully'),
      icon: 'check',
      iconClasses: 'text-green-600',
    })
  })

  if (quotation.data) {
    organization.data = quotation.data._organizationObj
    return
  }
  quotation.fetch()
})

onBeforeUnmount(() => {
  $socket.off('crm_customer_created')
})

const reload = ref(false)
const showOrganizationModal = ref(false)
const showAssignmentModal = ref(false)
const showSidePanelModal = ref(false)
const showFilesUploader = ref(false)
const _organization = ref({})

function updateField(fieldname, value, callback) {
  value = Array.isArray(fieldname) ? '' : value

  if (validateRequired(fieldname, value)) return

  createResource({
    url: 'frappe.client.set_value',
    params: {
      doctype: 'CRM Quotation',
      name: props.quotationId,
      fieldname,
      value,
    },
    auto: true,
    onSuccess: () => {
      quotation.reload()
      reload.value = true
      createToast({
        title: __('Quotation updated'),
        icon: 'check',
        iconClasses: 'text-green-600',
      })
      callback?.()
    },
    onError: (err) => {
      createToast({
        title: __('Error updating quotation'),
        text: __(err.messages?.[0]),
        icon: 'x',
        iconClasses: 'text-red-600',
      })
    },
  })
}

function validateRequired(fieldname, value) {
  let meta = quotation.data.fields_meta || {}
  if (meta[fieldname]?.reqd && !value) {
    createToast({
      title: __('Error Updating Quotation'),
      text: __('{0} is a required field', [meta[fieldname].label]),
      icon: 'x',
      iconClasses: 'text-red-600',
    })
    return true
  }
  return false
}

const breadcrumbs = computed(() => {
  let items = [{ label: __('Quotations'), route: { name: 'Quotations' } }]

  if (route.query.view || route.query.viewType) {
    let view = getView(route.query.view, route.query.viewType, 'CRM Quotation')
    if (view) {
      items.push({
        label: __(view.label),
        icon: view.icon,
        route: {
          name: 'Quotations',
          params: { viewType: route.query.viewType },
          query: { view: route.query.view },
        },
      })
    }
  }

  items.push({
    label: organization.data?.name || __('Untitled'),
    route: { name: 'Quotation', params: { quotationId: quotation.data.name } },
  })
  return items
})

usePageMeta(() => {
  return {
    title: quotation.data ? `${__('Quotation')} - ${quotation.data.name}` : __('Quotation'),
    emoji: '📄'
  }
})

const activities = ref(null)

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
      name: 'Data',
      label: __('Data'),
      icon: DetailsIcon,
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
    {
      name: 'WhatsApp',
      label: __('WhatsApp'),
      icon: WhatsAppIcon,
      condition: () => whatsappEnabled.value,
    },
  ]
  return tabOptions.filter((tab) => (tab.condition ? tab.condition() : true))
})

const { tabIndex } = useActiveTabManager(tabs, 'lastQuotationTab')

const fieldsLayout = createResource({
  url: 'lg.lg.doctype.crm_quotation.api.get_fields_layout',
  cache: ['fieldsLayout', props.quotationId],
  params: { name: props.quotationId },
  auto: true,
  transform: (data) => {
    if (!data) return []
    return data.map(section => ({
      ...section,
      opened: true,
      fields: section.fields.map(field => ({
        ...field,
        value: quotation.data?.[field.fieldname]
      }))
    }))
  },
  onError: (error) => {
    createToast({
      title: __('Error loading fields'),
      text: error.message,
      icon: 'x',
      iconClasses: 'text-red-600',
    })
  },
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

const showContactModal = ref(false)
const _contact = ref({})

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

const quotationContacts = createResource({
  url: 'lg.lg.doctype.crm_quotation.api.get_quotation_contacts',
  params: { name: props.quotationId },
  cache: ['quotation_contacts', props.quotationId],
  auto: true,
  onError: (error) => {
    createToast({
      title: __('Error loading contacts'),
      text: error.message,
      icon: 'x',
      iconClasses: 'text-red-600',
    })
  },
  transform: (data) => {
    if (!Array.isArray(data)) return []
    return data.map((contact) => ({
      ...contact,
      opened: false
    }))
  },
})

async function addContact(contact) {
  let d = await call('lg.lg.doctype.crm_quotation.api.add_contact', {
    quotation: props.quotationId,
    contact,
  })
  if (d) {
    quotationContacts.reload()
    createToast({
      title: __('Contact added'),
      icon: 'check',
      iconClasses: 'text-green-600',
    })
  }
}

async function removeContact(contact) {
  let d = await call('lg.lg.doctype.crm_quotation.api.remove_contact', {
    quotation: props.quotationId,
    contact,
  })
  if (d) {
    quotationContacts.reload()
    createToast({
      title: __('Contact removed'),
      icon: 'check',
      iconClasses: 'text-green-600',
    })
  }
}

async function setPrimaryContact(contact) {
  let d = await call('lg.lg.doctype.crm_quotation.api.set_primary_contact', {
    quotation: props.quotationId,
    contact,
  })
  if (d) {
    quotationContacts.reload()
    createToast({
      title: __('Primary contact set'),
      icon: 'check',
      iconClasses: 'text-green-600',
    })
  }
}

function triggerCall() {
  let primaryContact = quotationContacts.data?.find((c) => c.is_primary)
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

function openEmailBox() {
  if (!quotation.data.email) {
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

// Add new computed properties
const showKPICards = computed(() => {
  return !route.query.hideKPI
})

const isExpiringSoon = computed(() => {
  if (!quotation.data?.valid_till) return false
  const validTill = new Date(quotation.data.valid_till)
  const today = new Date()
  const daysUntilExpiry = Math.ceil((validTill - today) / (1000 * 60 * 60 * 24))
  return daysUntilExpiry <= 7 && daysUntilExpiry > 0
})

async function deleteQuotation() {
  try {
    await call('lg.lg.doctype.crm_quotation.api.delete_quotation', {
      name: props.quotationId
    })
    router.push({ name: 'Quotations' })
    createToast({
      title: __('Quotation deleted'),
      icon: 'check',
      iconClasses: 'text-green-600',
    })
  } catch (error) {
    createToast({
      title: __('Error deleting quotation'),
      text: error.message,
      icon: 'x',
      iconClasses: 'text-red-600',
    })
  }
}

function formatAmount(amount, currency) {
  if (!amount || !currency) return ''
  return formatCurrency(amount, currency)
}

// Add function to get status color class based on the status color
function getStatusColorClass(color) {
  if (!color) return 'text-gray-600 bg-gray-100 hover:bg-gray-200'
  return `text-${color}-600 bg-${color}-100 hover:bg-${color}-200`
}

// Add function to get quotation status details
function getQuotationStatusDetails(statusDoc) {
  if (!statusDoc) return { 
    colorClass: 'text-gray-600 bg-gray-100 hover:bg-gray-200',
    theme: 'gray',
    variant: 'solid'
  }
  return {
    colorClass: getStatusColorClass(statusDoc.color),
    theme: statusDoc.color || 'gray',
    variant: 'solid'
  }
}

const quotationStatusOptions = computed(() => {
  if (!quotation.data?.status_options) {
    // Fetch available statuses if not present
    createResource({
      url: 'frappe.client.get_list',
      params: {
        doctype: 'CRM Quotation Status',
        fields: ['name', 'status', 'color', 'position'],
        order_by: 'position asc'
      },
      auto: true,
      onSuccess: (data) => {
        quotation.data.status_options = data
      }
    })
    return []
  }
  
  return quotation.data.status_options.map(status => ({
    label: status.status || status.name,
    value: status.name,
    icon: () => h(IndicatorIcon, { class: getStatusColorClass(status.color) }),
    onClick: () => updateField('status', status.name)
  }))
})

const attachments = createResource({
  url: 'frappe.client.get_list',
  params: {
    doctype: 'File',
    filters: {
      attached_to_doctype: 'CRM Quotation',
      attached_to_name: props.quotationId,
    },
    fields: ['name', 'file_name', 'file_url', 'is_private', 'file_size', 'creation', 'file_type'],
  },
  auto: true,
})
</script>


<style scoped>
:deep(.section:has(.section-field.hidden)) {
  display: none;
}
:deep(.section:has(.section-field:not(.hidden))) {
  display: flex;
}

.quotation-card {
  @apply m-4 rounded-lg border border-gray-200 bg-white p-6;
}

.card-title {
  @apply text-lg font-medium text-gray-900;
}

.field-label {
  @apply text-sm font-medium text-gray-500;
}

.field-value {
  @apply mt-1 text-sm text-gray-900;
}

.grid-layout {
  @apply grid grid-cols-1 gap-4;
}

.grid-layout-2 {
  @apply sm:grid-cols-2;
}

.grid-layout-3 {
  @apply sm:grid-cols-3;
}
</style>