<template>
  <LayoutHeader>
    <template #left-header>
      <ViewBreadcrumbs v-model="viewControls" routeName="Opportunity" />
    </template>
    <template #right-header>
      <CustomActions
        v-if="serialsListView?.customListActions"
        :actions="serialsListView.customListActions"
      />
      <Button
        variant="solid"
        :label="__('Create')"
        @click="showSerialModal = true"
      >
        <template #prefix><FeatherIcon name="plus" class="h-4" /></template>
      </Button>
    </template>
  </LayoutHeader>

  <ViewControls
    ref="viewControls"
    v-model="tasks.data"
    v-model:loadMore="loadMore"
    v-model:resizeColumn="triggerResize"
    v-model:updatedPageCount="updatedPageCount"
    doctype="Serial No"
    :options="{ allowedViews: ['list', 'group_by'] }"
  />

  <!-- List View -->
  <DealsListView
    ref="dealsListView"
    v-if="tasks.data && rows.length"
    v-model="tasks.data"
    v-model:list="tasks.data"
    :rows="rows"
    :columns="columns"
    :options="{
      showTooltip: false,
      resizeColumn: true,
      rowCount: tasks.data.length,
      totalCount: tasks.data.length,
    }"
    @loadMore="() => loadMore++"
    @columnWidthUpdated="() => triggerResize++"
  />

  <div v-else class="flex h-full items-center justify-center">
    <div class="flex flex-col items-center gap-3 text-xl font-medium text-gray-500">
      <DealsIcon class="h-10 w-10" />
      <span>{{ __('No {0} Found', [__('Serials')]) }}</span>
      <Button :label="__('Create')" @click="showSerialModal = true">
        <template #prefix><FeatherIcon name="plus" class="h-4" /></template>
      </Button>
    </div>
  </div>

  <SerialModal
    v-if="showSerialModal"
    v-model="showSerialModal"
    v-model:quickEntry="showQuickEntryModal"
    :defaults="defaults"
  />
</template>
<script setup>
import ViewBreadcrumbs from '@/components/ViewBreadcrumbs.vue'
import MultipleAvatar from '@/components/MultipleAvatar.vue'
import CustomActions from '@/components/CustomActions.vue'
import EmailAtIcon from '@/components/Icons/EmailAtIcon.vue'
import PhoneIcon from '@/components/Icons/PhoneIcon.vue'
import NoteIcon from '@/components/Icons/NoteIcon.vue'
import TaskIcon from '@/components/Icons/TaskIcon.vue'
import CommentIcon from '@/components/Icons/CommentIcon.vue'
import IndicatorIcon from '@/components/Icons/IndicatorIcon.vue'
import DealsIcon from '@/components/Icons/DealsIcon.vue'
import LayoutHeader from '@/components/LayoutHeader.vue'
import SerialListView from '@/components/ListViews/SerialListView.vue'
import KanbanView from '@/components/Kanban/KanbanView.vue'
import DealModal from '@/components/Modals/DealModal.vue'
import NoteModal from '@/components/Modals/NoteModal.vue'
import TaskModal from '@/components/Modals/TaskModal.vue'
import QuickEntryModal from '@/components/Modals/QuickEntryModal.vue'
import ViewControls from '@/components/ViewControls.vue'
import { globalStore } from '@/stores/global'
import { usersStore } from '@/stores/users'
import { organizationsStore } from '@/stores/organizations'
import { statusesStore } from '@/stores/statuses'
import { callEnabled } from '@/composables/settings'
import {
  dateFormat,
  dateTooltipFormat,
  timeAgo,
  website,
  formatNumberIntoCurrency,
  formatTime,
} from '@/utils'

import { Tooltip, Avatar, Dropdown } from 'frappe-ui'
import { useRoute } from 'vue-router'
import { ref, reactive, computed, h } from 'vue'

const { makeCall } = globalStore()
const { getUser } = usersStore()
const { getOrganization } = organizationsStore()
const { getSerialStatus } = statusesStore()

const route = useRoute()

const serialListView = ref(null)
const showSerialModal = ref(false)
const showQuickEntryModal = ref(false)

const defaults = reactive({})

// serials data is loaded in the ViewControls component

// serials is now changes to serials 
const serials = ref({})
const loadMore = ref(1)
const triggerResize = ref(1)
const updatedPageCount = ref(20)
const viewControls = ref(null)

function getRow(name, field) {
  function getValue(value) {
    if (value && typeof value === 'object' && !Array.isArray(value)) {
      return value
    }
    return { label: value }
  }
  return getValue(rows.value?.find((row) => row.name == name)[field])
}

// Rows
const rows = computed(() => {
  if (!serials.value?.data?.data) return []
  if (serials.value.data.view_type === 'group_by') {
    if (!serials.value?.data.group_by_field?.name) return []
    return getGroupedByRows(
      serials.value?.data.data,
      serials.value?.data.group_by_field,
    )
  } else if (serials.value.data.view_type === 'kanban') {
    return getKanbanRows(serials.value.data.data)
  } else {
    return parseRows(serials.value?.data.data)
  }
})

function getGroupedByRows(listRows, groupByField) {
  let groupedRows = []

  groupByField.options?.forEach((option) => {
    let filteredRows = []

    if (!option) {
      filteredRows = listRows.filter((row) => !row[groupByField.name])
    } else {
      filteredRows = listRows.filter((row) => row[groupByField.name] == option)
    }

    let groupDetail = {
      label: groupByField.label,
      group: option || __(' '),
      collapsed: false,
      rows: parseRows(filteredRows),
    }
    if (groupByField.name == 'status') {
      groupDetail.icon = () =>
        h(IndicatorIcon, {
          class: getSerialStatus(option)?.iconColorClass,
        })
    }
    groupedRows.push(groupDetail)
  })

  return groupedRows || listRows
}

function getKanbanRows(data) {
  let _rows = []
  data.forEach((column) => {
    column.data?.forEach((row) => {
      _rows.push(row)
    })
  })
  return parseRows(_rows)
}


// deal is now changes to serial 

function parseRows(rows) {
  return rows.map((serial) => {
    let _rows = {};

    rows.forEach((row) => {
      _rows[row] = serial[row];

      if (row === 'serial_no') {
        _rows[row] = {
          label: serial.serial_no,
          // logo: getOrganization(serial.serial_no)?.serial_no_logo,
        };
      } else if (row === 'status') {
        _rows[row] = {
          label: serial.status,
          // color: getDealStatus(serial.status)?.iconColorClass,
        };
      } else if (row === 'product_name') {
        _rows[row] = {
          label: serial.product_name,
          // && getUser(serial.deal_owner).full_name,
          // ...(serial.deal_owner && getUser(serial.deal_owner)),
        };
      } else if (row === 'product_group') {
        _rows[row] = {
          label: serial.product_group,
        };
      } else if (row === 'product_code') {
        _rows[row] = {
          label: serial.product_code,
        };
      } else if (['start_date', 'expiry_date'].includes(row)) {
        _rows[row] = {
          label: dateFormat(serial[row], dateTooltipFormat),
          timeAgo: __(timeAgo(serial[row])),
        };
      }
    });

    return _rows;
  });
}
</script>


<style scope>
</style>