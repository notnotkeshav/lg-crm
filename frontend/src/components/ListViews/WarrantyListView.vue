<template>
  <ListView
    :class="$attrs.class"
    :columns="columns"
    :rows="rows"
    :options="{
      getRowRoute: (row) => ({
        name: 'Warranty',
        params: { warrantyId: row.name },
        query: { view: route.query.view, viewType: route.params.viewType },
      }),
      selectable: options.selectable,
      showTooltip: options.showTooltip,
      resizeColumn: options.resizeColumn,
      getActions: (row) => getRowActions(row),
    }"
    row-key="name"
    @select="handleSelect"
  >
    <ListHeader
      class="sm:mx-5 mx-3"
      @columnWidthUpdated="emit('columnWidthUpdated')"
    >
      <ListHeaderItem
        v-for="column in columns"
        :key="column.key"
        :item="column"
        @columnWidthUpdated="emit('columnWidthUpdated', column)"
      >
        <Button
          v-if="column.key == '_liked_by'"
          variant="ghosted"
          class="!h-4"
          :class="isLikeFilterApplied ? 'fill-red-500' : 'fill-white'"
          @click="() => emit('applyLikeFilter')"
        >
          <HeartIcon class="h-4 w-4" />
        </Button>
      </ListHeaderItem>
    </ListHeader>

    <ListRows :rows="rows" v-slot="{ idx, column, item, row }">
      <ListRowItem
        :idx="idx"
        :column="column"
        :item="item"
        :row="row"
        :options="{
          showTooltip: options.showTooltip,
        }"
      >
        <template v-if="column.key === 'name'">
          <div class="flex items-center gap-3">
            <div class="flex-1 min-w-0">
              <div class="font-medium truncate">{{ row.name }}</div>
              <div class="text-sm text-gray-600">
                {{ row.customer_name }}
              </div>
            </div>
          </div>
        </template>

        <template v-else-if="column.key === 'warranty_status'">
          <div class="flex items-center gap-2">
            <IndicatorIcon
              :color="getStatusColor(row.warranty_status)"
              class="h-4 w-4"
            />
            <span>{{ row.warranty_status }}</span>
          </div>
        </template>

        <template v-else-if="column.key === 'warranty_owner'">
          <div class="flex items-center gap-2">
            <Avatar
              v-if="row.warranty_owner"
              :image="row.warranty_owner_image"
              :label="row.warranty_owner_name"
              size="sm"
            />
            <span>{{ row.warranty_owner_name || row.warranty_owner }}</span>
          </div>
        </template>

        <template v-else-if="column.key === 'organization'">
          <div class="flex items-center gap-2">
            <Avatar
              v-if="row.organization"
              :image="row.organization_logo"
              :label="row.organization"
              size="sm"
            />
            <span>{{ row.organization }}</span>
          </div>
        </template>

        <template v-else-if="column.key === '_liked_by'">
          <Button
            variant="ghosted"
            class="!h-4"
            :class="isDocLiked(row) ? 'fill-red-500' : 'fill-white'"
            @click.stop="() => emit('likeDoc', row)"
          >
            <HeartIcon class="h-4 w-4" />
          </Button>
        </template>

        <template v-else-if="column.key === 'modified'">
          <Tooltip :text="formatDate(row.modified, dateTooltipFormat)">
            {{ timeAgo(row.modified) }}
          </Tooltip>
        </template>

        <template v-else-if="['creation', 'expiry_date'].includes(column.key)">
          <Tooltip :text="formatDate(row[column.key], dateTooltipFormat)">
            {{ timeAgo(row[column.key]) }}
          </Tooltip>
        </template>
      </ListRowItem>
    </ListRows>

    <template #banner>
      <ListSelectBanner
        :selected="selected"
        :total="rows.length"
        @clear="clearSelection"
      >
        <template #actions>
          <ListBulkActions
            :selected="selected"
            :actions="getBulkActions()""
          />
        </template>
      </ListSelectBanner>
    </template>

    <template #footer>
      <ListFooter
        :options="options"
        @loadMore="emit('loadMore')"
        @updatePageCount="emit('updatePageCount', $event)"
      />
    </template>
  </ListView>
</template>

<script setup>
import HeartIcon from '@/components/Icons/HeartIcon.vue'
import IndicatorIcon from '@/components/Icons/IndicatorIcon.vue'
import ListBulkActions from '@/components/ListBulkActions.vue'
import ListRows from '@/components/ListViews/ListRows.vue'
import {
  Avatar,
  ListView,
  ListHeader,
  ListHeaderItem,
  ListRowItem,
  ListSelectBanner,
  ListFooter,
  Button,
  Dropdown,
  Tooltip,
} from 'frappe-ui'
import { sessionStore } from '@/stores/session'
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import { formatDate, dateTooltipFormat, timeAgo } from '@/utils'

const props = defineProps({
  rows: {
    type: Array,
    required: true,
  },
  columns: {
    type: Array,
    required: true,
  },
  options: {
    type: Object,
    default: () => ({
      selectable: true,
      showTooltip: true,
      resizeColumn: false,
      totalCount: 0,
      rowCount: 0,
    }),
  },
})

const emit = defineEmits([
  'loadMore',
  'updatePageCount',
  'columnWidthUpdated',
  'applyFilter',
  'applyLikeFilter',
  'likeDoc',
  'delete',
  'select',
  'addNote',
  'sendEmail',
])

const route = useRoute()
const selected = ref([])

const isLikeFilterApplied = computed(() => {
  return route.query._liked_by === sessionStore.user.name
})

function isDocLiked(row) {
  return row._liked_by?.includes(sessionStore.user.name)
}

function getStatusColor(status) {
  const colors = {
    'Active': 'green',
    'Expired': 'red',
    'Pending': 'orange',
    'Draft': 'gray',
    'Cancelled': 'red',
  }
  return colors[status] || 'gray'
}

function handleSelect(rows) {
  selected.value = rows
  emit('select', rows)
}

function getRowActions(row) {
  return [
    {
      label: __('Add Note'),
      icon: 'note',
      onClick: () => emit('addNote', row),
    },
    {
      label: __('Send Email'),
      icon: 'mail',
      onClick: () => emit('sendEmail', row),
    },
    {
      label: __('Delete'),
      icon: 'trash',
      variant: 'danger',
      onClick: () => emit('delete', [row.name]),
    },
  ]
}

function getBulkActions() {
  return [
    {
      label: __('Delete'),
      variant: 'danger',
      icon: 'trash',
      action: () => emit('delete', selected.value),
    },
    {
      label: __('Send Email'),
      icon: 'mail',
      action: () => emit('sendEmail', selected.value),
    },
  ]
}

function clearSelection() {
  selected.value = []
}

defineExpose({
  selected,
  clearSelection,
})
</script>