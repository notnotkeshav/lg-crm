<template>
  <LayoutHeader>
    <template #left-header>
      <ViewBreadcrumbs v-model="viewControls" routeName="Warranty" />
    </template>
    <template #right-header>
      <CustomActions
        v-if="warrantyListView?.customListActions"
        :actions="warrantyListView.customListActions"
      />
      <Button
        variant="solid"
        :label="__('Create')"
        @click="showWarrantyModal = true"
      >
        <template #prefix><FeatherIcon name="plus" class="h-4" /></template>
      </Button>
    </template>
  </LayoutHeader>
  <ViewControls
    ref="viewControls"
    v-model="warranties"
    v-model:loadMore="loadMore"
    v-model:resizeColumn="triggerResize"
    v-model:updatedPageCount="updatedPageCount"
    doctype="Warranty"
    :options="{
      allowedViews: ['list', 'group_by', 'kanban'],
    }"
  />
  <KanbanView
    v-if="route.params.viewType == 'kanban'"
    v-model="warranties"
    :options="{
      getRoute: (row) => ({
        name: 'Warranty',
        params: { warrantyId: row.name },
        query: { view: route.query.view, viewType: route.params.viewType },
      }),
      onNewClick: (column) => onNewClick(column),
    }"
    @update="(data) => viewControls.updateKanbanSettings(data)"
    @loadMore="(columnName) => viewControls.loadMoreKanban(columnName)"
  >
    <template #title="{ titleField, itemName }">
      <div class="flex gap-2 items-center">
        <div v-if="titleField === 'status'">
          <IndicatorIcon :class="getRow(itemName, titleField).color" />
        </div>
        <div
          v-else-if="
            titleField === 'organization' && getRow(itemName, titleField).label
          "
        >
          <Avatar
            class="flex items-center"
            :image="getRow(itemName, titleField).logo"
            :label="getRow(itemName, titleField).label"
            size="sm"
          />
        </div>
        <div
          v-else-if="
            titleField === 'warranty_owner' &&
            getRow(itemName, titleField).full_name
          "
        >
          <Avatar
            class="flex items-center"
            :image="getRow(itemName, titleField).user_image"
            :label="getRow(itemName, titleField).full_name"
            size="sm"
          />
        </div>
        <div
          v-if="['modified', 'creation', 'expiry_date'].includes(titleField)"
          class="truncate text-base"
        >
          <Tooltip :text="getRow(itemName, titleField).label">
            <div>{{ getRow(itemName, titleField).timeAgo }}</div>
          </Tooltip>
        </div>
        <div
          v-else-if="getRow(itemName, titleField).label"
          class="truncate text-base"
        >
          {{ getRow(itemName, titleField).label }}
        </div>
        <div class="text-gray-500" v-else>{{ __('No Title') }}</div>
      </div>
    </template>

    <template #fields="{ fieldName, itemName }">
      <div
        v-if="getRow(itemName, fieldName).label"
        class="truncate flex items-center gap-2"
      >
        <div v-if="fieldName === 'status'">
          <IndicatorIcon :class="getRow(itemName, fieldName).color" />
        </div>
        <div v-else-if="fieldName === 'organization'">
          <Avatar
            v-if="getRow(itemName, fieldName).label"
            class="flex items-center"
            :image="getRow(itemName, fieldName).logo"
            :label="getRow(itemName, fieldName).label"
            size="xs"
          />
        </div>
        <div v-else-if="fieldName === 'warranty_owner'">
          <Avatar
            v-if="getRow(itemName, fieldName).full_name"
            class="flex items-center"
            :image="getRow(itemName, fieldName).user_image"
            :label="getRow(itemName, fieldName).full_name"
            size="xs"
          />
        </div>
        <div
          v-if="['modified', 'creation', 'expiry_date'].includes(fieldName)"
          class="truncate text-base"
        >
          <Tooltip :text="getRow(itemName, fieldName).label">
            <div>{{ getRow(itemName, fieldName).timeAgo }}</div>
          </Tooltip>
        </div>
        <div v-else class="truncate text-base">
          {{ getRow(itemName, fieldName).label }}
        </div>
      </div>
    </template>

    <template #actions="{ itemName }">
      <div class="flex gap-2 items-center justify-between">
        <div class="text-gray-600 flex items-center gap-1.5">
          <EmailAtIcon class="h-4 w-4" />
          <span v-if="getRow(itemName, '_email_count').label">
            {{ getRow(itemName, '_email_count').label }}
          </span>
          <span class="text-3xl leading-[0]"> &middot; </span>
          <NoteIcon class="h-4 w-4" />
          <span v-if="getRow(itemName, '_note_count').label">
            {{ getRow(itemName, '_note_count').label }}
          </span>
          <span class="text-3xl leading-[0]"> &middot; </span>
          <CommentIcon class="h-4 w-4" />
          <span v-if="getRow(itemName, '_comment_count').label">
            {{ getRow(itemName, '_comment_count').label }}
          </span>
        </div>
        <Dropdown
          class="flex items-center gap-2"
          :options="actions(itemName)"
          variant="ghost"
          @click.stop.prevent
        >
          <Button icon="plus" variant="ghost" />
        </Dropdown>
      </div>
    </template>
  </KanbanView>
  <WarrantyListView
    ref="warrantyListView"
    v-else-if="warranties.data && rows.length"
    v-model="warranties.data.page_length_count"
    v-model:list="warranties"
    :rows="rows"
    :columns="warranties.data.columns"
    :options="{
      showTooltip: false,
      resizeColumn: true,
      rowCount: warranties.data.row_count,
      totalCount: warranties.data.total_count,
    }"
    @loadMore="() => loadMore++"
    @columnWidthUpdated="() => triggerResize++"
    @updatePageCount="(count) => (updatedPageCount = count)"
    @applyFilter="(data) => viewControls.applyFilter(data)"
    @applyLikeFilter="(data) => viewControls.applyLikeFilter(data)"
    @likeDoc="(data) => viewControls.likeDoc(data)"
  />
  <div v-else-if="warranties.data" class="flex h-full items-center justify-center">
    <div
      class="flex flex-col items-center gap-3 text-xl font-medium text-gray-500"
    >
      <WarrantyIcon class="h-10 w-10" />
      <span>{{ __('No {0} Found', [__('Warranties')]) }}</span>
      <Button :label="__('Create')" @click="showWarrantyModal = true">
        <template #prefix><FeatherIcon name="plus" class="h-4" /></template>
      </Button>
    </div>
  </div>
  <WarrantyModal
    v-if="showWarrantyModal"
    v-model="showWarrantyModal"
    :defaults="defaults"
  />
  <NoteModal
    v-if="showNoteModal"
    v-model="showNoteModal"
    :note="note"
    doctype="Warranty"
    :doc="docname"
  />
</template>

<script setup>
import ViewBreadcrumbs from '@/components/ViewBreadcrumbs.vue'
import MultipleAvatar from '@/components/MultipleAvatar.vue'
import CustomActions from '@/components/CustomActions.vue'
import EmailAtIcon from '@/components/Icons/EmailAtIcon.vue'
import NoteIcon from '@/components/Icons/NoteIcon.vue'
import CommentIcon from '@/components/Icons/CommentIcon.vue'
import IndicatorIcon from '@/components/Icons/IndicatorIcon.vue'
import WarrantyIcon from '@/components/Icons/WarrantyIcon.vue'
import LayoutHeader from '@/components/LayoutHeader.vue'
import WarrantyListView from '@/components/ListViews/WarrantyListView.vue'
import KanbanView from '@/components/Kanban/KanbanView.vue'
import WarrantyModal from '@/components/Modals/WarrantyModal.vue'
import NoteModal from '@/components/Modals/NoteModal.vue'
import ViewControls from '@/components/ViewControls.vue'
import { usersStore } from '@/stores/users'
import { organizationsStore } from '@/stores/organizations'
import { dateFormat, dateTooltipFormat, timeAgo } from '@/utils'
import { Tooltip, Avatar, Dropdown, Button, FeatherIcon } from 'frappe-ui'
import { useRoute, useRouter } from 'vue-router'
import { ref, reactive, computed, watch, h } from 'vue'

const { getUser } = usersStore()
const { getOrganization } = organizationsStore()

const route = useRoute()
const router = useRouter()

const warrantyListView = ref(null)
const showWarrantyModal = ref(false)
const defaults = reactive({})

// warranties data is loaded in the ViewControls component
const warranties = ref({})
const loadMore = ref(1)
const triggerResize = ref(1)
const updatedPageCount = ref(20)
const viewControls = ref(null)

// Watch for view type changes
watch(
  () => route.params.viewType,
  (newViewType) => {
    if (viewControls.value) {
      viewControls.value.setViewType(newViewType || 'list')
    }
  },
  { immediate: true }
)

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
  if (!warranties.value?.data?.data) return []
  if (warranties.value.data.view_type === 'group_by') {
    if (!warranties.value?.data.group_by_field?.name) return []
    return getGroupedByRows(
      warranties.value?.data.data,
      warranties.value?.data.group_by_field,
    )
  } else if (warranties.value.data.view_type === 'kanban') {
    return getKanbanRows(warranties.value.data.data)
  } else {
    return parseRows(warranties.value?.data.data)
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

function parseRows(rows) {
  return rows.map((warranty) => {
    let _rows = {}
    warranties.value.data.rows.forEach((row) => {
      _rows[row] = warranty[row]

      if (row == 'organization') {
        _rows[row] = {
          label: warranty.organization,
          logo: getOrganization(warranty.organization)?.organization_logo,
        }
      } else if (row == 'warranty_owner') {
        _rows[row] = {
          label: warranty.warranty_owner && getUser(warranty.warranty_owner).full_name,
          ...(warranty.warranty_owner && getUser(warranty.warranty_owner)),
        }
      } else if (['modified', 'creation', 'expiry_date'].includes(row)) {
        _rows[row] = {
          label: dateFormat(warranty[row], dateTooltipFormat),
          timeAgo: __(timeAgo(warranty[row])),
        }
      }
    })
    _rows['_email_count'] = warranty._email_count
    _rows['_note_count'] = warranty._note_count
    _rows['_comment_count'] = warranty._comment_count
    return _rows
  })
}

function onNewClick(column) {
  let column_field = warranties.value.params.column_field

  if (column_field) {
    defaults[column_field] = column.column.name
  }

  showWarrantyModal.value = true
}

function actions(itemName) {
  let actions = [
    {
      icon: h(NoteIcon, { class: 'h-4 w-4' }),
      label: __('New Note'),
      onClick: () => showNote(itemName),
    }
  ]
  return actions
}

const docname = ref('')
const showNoteModal = ref(false)
const note = ref({
  title: '',
  content: '',
})

function showNote(name) {
  docname.value = name
  showNoteModal.value = true
}

// Handle route changes for view types
function handleViewTypeChange(viewType) {
  router.push({
    name: 'WarrantiesView',
    params: { viewType: viewType || 'list' },
    query: route.query
  })
}

// Expose necessary methods to template
defineExpose({
  handleViewTypeChange
})
</script>